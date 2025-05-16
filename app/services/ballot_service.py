import logging
from datetime import date, timedelta
from typing import Optional, List
import random
from app.schemas.ballots import BallotResponse, BallotCreate
from app.schemas.participant import ParticipantResponse
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
from app.models.ballot import (
  Ballot, 
)
from app.models.lottery import (
    Lottery,
)
from app.middleware.exceptions.ballot_service_exceptions import (
    BallotServiceError,
    BallotCreationError,
    BallotsNotFoundErrorForUser
)
from app.middleware.exceptions.lottery_service_exceptions import (
    LotteryCreationError as LotteryServiceCreationError,
    LotteryNotFoundError
)
logger = logging.getLogger("app")

class BallotService:
    def __init__(
        self,
        # Repositories are now directly injected
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

    def _get_or_create_lottery_for_ballot(self, target_date: date) -> Lottery:
        """
        Helper to get an existing open lottery for a date, or create one if it doesn't exist.
        Raises:
            LotteryServiceCreationError: If lottery creation fails.
        """
        lottery: Optional[Lottery] = self.lottery_repo.get_by_date(target_date)
        if not lottery:
            logger.debug("No lottery found for %s, creating new one for ballot submission.", target_date)
            try:
                lottery = self.lottery_repo.create_lottery(input_date=target_date)
                if not lottery:
                    raise LotteryServiceCreationError(target_date, "Repository returned None during implicit creation.")
                logger.info("Implicitly created lottery %s for date %s", lottery.lottery_id, target_date)
            except Exception as e: 
                logger.error(f"Implicit lottery creation failed for ballot on date {target_date}: {e}")
                raise LotteryServiceCreationError(target_date, f"Implicit creation failed: {str(e)}")
        return lottery

    
    def create_ballot(self, user_id: int) -> BallotResponse:
        """
        Submits a new ballot for today's lottery; creates the lottery if missing.
        """
        # FIXME: REMOVE TIMEDELTA FROM HERE TO GET CORRECT BEHAVIOUR THIS IS ONLY FOR DEV PURPOSES
        target_date: date = date.today() - timedelta(days=1)
        logger.info("Submitting ballot for user %s on %s", user_id, target_date)

        lottery = self._get_or_create_lottery_for_ballot(target_date)

        try:
            ballot_model = self.ballot_repo.create_ballot(
                user_id=user_id,
                lottery_id=lottery.lottery_id,
                expiry_date=target_date
            )
            if not ballot_model:
                raise BallotCreationError(user_id, lottery.lottery_id, "Repository returned None.")
        except Exception as e:
            logger.error(f"Ballot creation in repository failed for user {user_id}, lottery {lottery.lottery_id}: {e}")
            raise BallotCreationError(user_id, lottery.lottery_id, str(e))

        response = BallotResponse.model_validate(ballot_model)
        logger.info("Ballot %s submitted successfully for lottery %s (user %s)",
                    ballot_model.ballot_id, lottery.lottery_id, user_id)
        return response

    def create_ballot_with_date(self, req : BallotCreate ) -> BallotResponse:
        """
        Submits a new ballot for today's lottery; creates the lottery if missing.
        """
        # FIXME: REMOVE TIMEDELTA FROM HERE TO GET CORRECT BEHAVIOUR THIS IS ONLY FOR DEV PURPOSES
        today: date = date.today() - timedelta(days=1)
        logger.info("Submitting ballot for user %s on %s", req.user_id, today)
    
        lottery: Optional[Lottery] = self.lottery_repo.get_by_date(req.expiry_date)
        if lottery:
            try:
                ballot_model = self.ballot_repo.create_ballot(
                    user_id=req.user_id,
                    lottery_id=lottery.lottery_id,
                    expiry_date=req.target_date
                )
                if not ballot_model:
                    raise BallotCreationError(req.user_id, lottery.lottery_id, "Repository returned None.")
            except Exception as e:
                logger.error(f"Ballot creation in repository failed for user {req.user_id}, lottery {lottery.lottery_id}: {e}")
                raise BallotCreationError(req.user_id, lottery.lottery_id, str(e))

            response = BallotResponse.model_validate(ballot_model)
            logger.info("Ballot %s submitted successfully for lottery %s (user %s)",
                        ballot_model.ballot_id, lottery.lottery_id, req.user_id)
            return response
        logger.error(f"Ballot creation in service failed for user {req.user_id}")
        raise LotteryNotFoundError(identifier=req.expiry_date)

    def list_ballots_by_user(self, user_id: int) -> List[BallotResponse]:
        """
        Lists all ballots submitted by a given user.
        Raises:
            BallotsNotFoundErrorForUser: If the user has no registered ballots.
            BallotServiceError: For other repository/listing errors.
        """
        logger.debug(f"Listing ballots for user ID: {user_id}")
        try:
            ballot_models: List[Ballot] = self.ballot_repo.list_by_user(user_id=user_id)
            if not ballot_models:
                logger.info(f"No ballots found for user ID {user_id}.")
                raise BallotsNotFoundErrorForUser(user_id=user_id)

            ballot_list = [BallotResponse.model_validate(p) for p in ballot_models]
            logger.info(f"Found {len(ballot_list)} ballots for user ID {user_id}.")
            return ballot_list
        except BallotsNotFoundErrorForUser: 
            raise
        except Exception as e: 
            logger.error(f"Error listing ballots for user {user_id}: {e}")
            raise BallotServiceError(f"Could not retrieve ballots for user {user_id}: {str(e)}")


