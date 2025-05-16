import logging
from datetime import date, timedelta
from typing import Optional, List
import random
from app.db.database import db  
from app.schemas.ballots import BallotResponse
from app.schemas.lottery import LotteryResponse
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from app.repositories.participant_repository import (
   get_participant_repository_provider,
)
from app.repositories.lottery_repository import (
   get_lottery_repository_provider,
)
from app.repositories.ballot_repository import (
    get_ballot_repository_provider,
)
from app.repositories.winner_ballots_repository import (
    get_winning_ballot_repository_provider,
)
from app.repositories.interfaces.ballot_repo_interface import BallotRepositoryInterface
from app.repositories.interfaces.lottery_repo_interface import LotteryRepositoryInterface
from app.repositories.interfaces.participant_repo_interface import ParticipantRepositoryInterface
from app.repositories.interfaces.winner_ballots_repo_interface import WinningBallotRepositoryInterface
from app.schemas.winning_ballot import(
    WinningBallotResponse
)
from app.middleware.exceptions.lottery_service_exceptions import (
    LotteryAlreadyExistsError,
    LotteryServiceError, 
    LotteryNotFoundError,
    LotteryClosedError,
    NoBallotsFoundError,
    LotteryCreationError,
    LotteryUpdateError,
    WinnerPersistenceError,
    InvalidLotteryOperationError
)

logger = logging.getLogger("app")



class LotteryService:
    def __init__(
        self,
        participant_repo: ParticipantRepositoryInterface = Depends(get_participant_repository_provider),
        lottery_repo: LotteryRepositoryInterface = Depends(get_lottery_repository_provider),
        ballot_repo: BallotRepositoryInterface = Depends(get_ballot_repository_provider),
        winning_repo: WinningBallotRepositoryInterface = Depends(get_winning_ballot_repository_provider)
    ) -> None:
        self.participant_repo = participant_repo
        self.lottery_repo = lottery_repo
        self.ballot_repo = ballot_repo
        self.winning_repo = winning_repo
        logger.debug("Initialized LotteryService with repos: %s, %s, %s, %s",
                     self.participant_repo, self.lottery_repo, self.ballot_repo, self.winning_repo)


    def close_lottery_and_draw(self) -> Optional[WinningBallotResponse]:
        """
        Closes *yesterday’s* lottery (i.e., the one whose date was “today - 1 day”)
        and selects a random winning ballot. Returns the winning record, or None if:
          - no lottery existed for yesterday
          - it was already closed
          - there were no ballots
        """

        closing_date = date.today() - timedelta(days=1)
        logger.info("Running close_and_draw for lottery date %s", closing_date)

        lottery = self.lottery_repo.get_by_date(closing_date)
        if lottery is None:
            logger.info("No lottery found for %s; skipping close", closing_date)
            raise HTTPException(status_code=418, detail="No lottery found for given date")

        if lottery.closed:
            logger.info("Lottery %s (%s) already closed; skipping", lottery.lottery_id, closing_date)
            raise HTTPException(status_code=418, detail=" It’s already been closed")

        ballots = self.ballot_repo.list_by_lottery(lottery.lottery_id)
        if not ballots:
            logger.warning(
                "No ballots submitted for lottery %s on %s. Cannot draw a winner.",
                lottery.lottery_id, closing_date
            )
            try:
                self.lottery_repo.mark_as_closed(lottery.lottery_id)
                logger.info("Lottery %s marked as closed without a winner due to no ballots.", lottery.lottery_id)
            except Exception as e: 
                logger.error("Failed to mark lottery %s as closed after finding no ballots: %s", lottery.lottery_id, e)
            raise NoBallotsFoundError(lottery_id=lottery.lottery_id, lottery_date=closing_date)

        winner_ballot = random.choice(ballots)
        logger.info(
            "Selected winner ballot %s for lottery %s on %s",
            winner_ballot.ballot_id, lottery.lottery_id, closing_date
        )

        try:
            win_record_model = self.winning_repo.create_winning_ballot(
                lottery_id=lottery.lottery_id,
                ballot_id=winner_ballot.ballot_id,
                winning_date=closing_date,
            )
            if win_record_model is None: 
                 raise WinnerPersistenceError(lottery.lottery_id, winner_ballot.ballot_id, "Repository returned None")
            logger.info("Winning record created for lottery %s: ballot %s",
                        lottery.lottery_id, winner_ballot.ballot_id)
        except Exception as e:
            logger.error("Failed to persist winning ballot for lottery %s: %s", lottery.lottery_id, e)
            raise WinnerPersistenceError(lottery.lottery_id, winner_ballot.ballot_id, str(e))

        try:
            self.lottery_repo.mark_as_closed(lottery.lottery_id)
            logger.debug("Lottery %s marked as closed after successful draw.", lottery.lottery_id)
        except Exception as e: 
            logger.error("Failed to mark lottery %s as closed after draw and winner persistence: %s", lottery.lottery_id, e)
            raise LotteryUpdateError(lottery.lottery_id, "mark_as_closed", f"Failed after winner persistence: {str(e)}")

        return WinningBallotResponse.model_validate(win_record_model)

    def create_lottery(self, target_date: date) -> LotteryResponse:
        """
        Creates a new lottery for the specified date.
        Raises LotteryAlreadyExistsError if a lottery for that date already exists.
        Raises LotteryServiceError if creation fails.
        """
        logger.info(f"Attempting to create lottery for date: {target_date}")
        existing_lottery = self.lottery_repo.get_by_date(target_date)
        if existing_lottery:
            logger.warning(f"Lottery already exists for date {target_date} with ID {existing_lottery.lottery_id}")
            raise LotteryAlreadyExistsError(target_date)

        try:
            lottery_model = self.lottery_repo.create_lottery(input_date=target_date)
            if lottery_model is None: 
                logger.error(f"Repository returned None when creating lottery for date {target_date}.")
                raise LotteryCreationError(target_date, "Repository returned None.")
        except Exception as e:
            logger.error(f"Repository failed to create lottery for date {target_date}: {e}")
            raise LotteryCreationError(target_date, str(e))

        logger.info(f"Successfully created lottery ID {lottery_model.lottery_id} for date {target_date}")
        return LotteryResponse.model_validate(lottery_model)

    def get_lottery(self, lottery_id: int) -> LotteryResponse:
        """
        Retrieves a lottery by its ID.
        Raises LotteryNotFoundError if not found.
        """
        logger.debug(f"Fetching lottery by ID: {lottery_id}")
        lottery_model = self.lottery_repo.get_lottery(lottery_id)
        if lottery_model is None:
            logger.warning(f"Lottery with ID {lottery_id} not found.")
            raise LotteryNotFoundError(identifier=lottery_id)
        return LotteryResponse.model_validate(lottery_model)

    def get_lottery_by_target_date(self, target_date: date) -> LotteryResponse:
        """
        Retrieves a lottery by its target date.
        Raises LotteryNotFoundError if not found.
        """
        logger.debug(f"Fetching lottery by date: {target_date}")
        lottery_model = self.lottery_repo.get_by_date(target_date)
        if lottery_model is None:
            logger.warning(f"Lottery for date {target_date} not found.")
            raise LotteryNotFoundError(identifier=target_date)
        return LotteryResponse.model_validate(lottery_model)

    def get_all_lotteries(self) -> List[LotteryResponse]:
        """
        Retrieves all lotteries.
        """
        logger.debug("Fetching all lotteries.")
        try:
            lottery_models = self.lottery_repo.list_lotteries()
            return [LotteryResponse.model_validate(l) for l in lottery_models]
        except Exception as e:
            logger.error(f"Error fetching all lotteries: {e}")
            raise LotteryServiceError(f"Failed to retrieve all lotteries: {str(e)}")


    def get_open_lotteries(self) -> List[LotteryResponse]:
        """
        Retrieves all lotteries that are currently open (not closed).
        """
        logger.debug("Fetching all open lotteries.")
        try:
            all_lotteries = self.lottery_repo.list_lotteries()
            open_lotteries = [l for l in all_lotteries if not l.closed]
            return [LotteryResponse.model_validate(l) for l in open_lotteries]
        except Exception as e:
            logger.error(f"Error fetching open lotteries: {e}")
            raise LotteryServiceError(f"Failed to retrieve open lotteries: {str(e)}")


    def get_active_lottery_for_today(self) -> Optional[LotteryResponse]:
        """
        Retrieves the active (open) lottery for the current date.
        Returns None if no lottery exists for today or if it's already closed.
        """
        logger.debug("Fetching active lottery for today.")
        today = date.today()

        try:
            lottery_model = self.lottery_repo.get_by_date(today)
        except Exception as e:
            logger.error(f"Error fetching lottery for today ({today}): {e}")
            raise LotteryServiceError(f"Failed to retrieve open lotteries for today: {str(e)}")

        if lottery_model and not lottery_model.closed:
            return LotteryResponse.model_validate(lottery_model)
        
        if lottery_model and lottery_model.closed:
            logger.info(f"Lottery for today (ID: {lottery_model.lottery_id}) found but is closed.")
        elif not lottery_model:
            logger.info(f"No lottery found for today ({today}).")
