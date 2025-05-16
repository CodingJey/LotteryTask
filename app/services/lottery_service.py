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


    def close_lottery_and_draw(self) -> WinningBallotResponse: # Return type changed
        """
        Closes *yesterday’s* lottery (i.e., the one whose date was “today - 1 day”)
        and selects a random winning ballot.

        Note: This method relies on individual repository operations being atomic.
        Data consistency across multiple distinct repository calls (e.g., creating
        a winner, then closing the lottery) is not guaranteed by this method if an
        operation fails mid-sequence.

        Returns:
            WinningBallotResponse: The details of the winning ballot if one is drawn.

        Raises:
            HTTPException (status_code=404): If no lottery existed for yesterday.
            HTTPException (status_code=409): If the lottery for yesterday was already closed.
            NoBallotsFoundError: If the lottery was successfully closed (by its repository call)
                                 but had no ballots submitted.
            WinnerPersistenceError: If saving the winning ballot record fails.
            LotteryUpdateError: If updating the lottery's 'closed' status fails.
            # Other underlying database exceptions might propagate if not caught by repository layers.
        """
        closing_date = date.today() - timedelta(days=1)
        logger.info("Service: Attempting to close and draw for lottery date %s (session management ignored)", closing_date)

        lottery = self.lottery_repo.get_by_date(closing_date)
        if lottery is None:
            logger.warning("Service: No lottery found for %s; cannot close or draw.", closing_date)
            raise HTTPException(status_code=404, detail=f"No lottery found for given date: {closing_date}")

        if lottery.closed:
            logger.info("Service: Lottery %s (date %s) already closed; skipping.", lottery.lottery_id, closing_date)
            raise HTTPException(status_code=409, detail=f"Lottery for date {closing_date} (ID: {lottery.lottery_id}) is already closed.")

        ballots = self.ballot_repo.list_by_lottery(lottery.lottery_id)
        win_record_model = None 

        if not ballots:
            logger.warning(
                "Service: No ballots submitted for lottery %s on %s. Attempting to close without a winner.",
                lottery.lottery_id, closing_date
            )
            try:
                closed_lottery_no_ballots = self.lottery_repo.mark_as_closed(lottery.lottery_id)
                if not closed_lottery_no_ballots or not closed_lottery_no_ballots.closed:
                    raise LotteryUpdateError(
                        lottery_id=lottery.lottery_id,
                        operation="mark_as_closed_no_ballots",
                        reason="Repository failed to confirm lottery closure or returned an unexpected state."
                    )
                logger.info("Service: Lottery %s (assumed) marked as closed by repository (no ballots).", lottery.lottery_id)
                raise NoBallotsFoundError(lottery_id=lottery.lottery_id, lottery_date=closing_date)
            except NoBallotsFoundError:
                raise
            except Exception as e_close_no_ballot:
                logger.error(
                    "Service: Failed to process lottery %s closure (no ballots scenario): %s",
                    lottery.lottery_id, e_close_no_ballot, exc_info=True
                )
                if not isinstance(e_close_no_ballot, LotteryUpdateError):
                    raise LotteryUpdateError(
                        lottery_id=lottery.lottery_id,
                        operation="mark_as_closed_no_ballots",
                        reason=str(e_close_no_ballot)
                    ) from e_close_no_ballot
                else:
                    raise 

        winner_ballot = random.choice(ballots)
        logger.info(
            "Service: Selected winner ballot %s for lottery %s on %s",
            winner_ballot.ballot_id, lottery.lottery_id, closing_date
        )

        try:
            win_record_model = self.winning_repo.create_winning_ballot(
                lottery_id=lottery.lottery_id,
                ballot_id=winner_ballot.ballot_id,
                winning_date=closing_date,
            )
            if win_record_model is None:
                raise WinnerPersistenceError(lottery.lottery_id, winner_ballot.ballot_id, "Repository returned None upon winning ballot creation.")
            logger.info("Service: Winning record (assumed) created by repository for lottery %s: ballot %s",
                        lottery.lottery_id, winner_ballot.ballot_id)
        except Exception as e_persist:
            logger.error("Service: Failed to persist winning ballot for lottery %s: %s", lottery.lottery_id, e_persist, exc_info=True)
            raise WinnerPersistenceError(
                lottery_id=lottery.lottery_id,
                ballot_id=winner_ballot.ballot_id,
                reason=str(e_persist)
            ) from e_persist


        try:
            closed_lottery_with_winner = self.lottery_repo.mark_as_closed(lottery.lottery_id)
            if not closed_lottery_with_winner or not closed_lottery_with_winner.closed:
                raise LotteryUpdateError(
                    lottery_id=lottery.lottery_id,
                    operation="mark_as_closed_after_draw",
                    reason="Repository failed to confirm lottery closure or returned an unexpected state after draw."
                )
            logger.info("Service: Lottery %s (assumed) marked as closed by repository after successful draw.", lottery.lottery_id)
        except Exception as e_close_final:
            logger.error(
                "Service: CRITICAL - Failed to mark lottery %s as closed AFTER winner persistence. DATA INCONSISTENCY IS LIKELY: %s",
                lottery.lottery_id, e_close_final, exc_info=True
            )
            # A winner IS PERSISTED, but lottery closing FAILED.
            raise LotteryUpdateError(
                lottery_id=lottery.lottery_id,
                operation="mark_as_closed_after_draw_CRITICAL",
                reason=f"Winner persisted, but final lottery closure failed. Data inconsistency likely. Reason: {str(e_close_final)}"
            ) from e_close_final

        # If all individual repository operations succeeded in sequence:
        logger.info("Service: Lottery close and draw process for date %s completed all steps.", closing_date)
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
