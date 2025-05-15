import logging
from datetime import date, timedelta
from typing import Optional, List
import random
from app.schemas.ballots import BallotResponse
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

logger = logging.getLogger("app.lottery")
logger.setLevel(logging.INFO)


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

    
    def create_ballot(self, user_id: int) -> BallotResponse:
        """
        Submits a new ballot for today's lottery; creates the lottery if missing.
        """
        # FIXME: REMOVE TIMEDELTA FROM HERE TO GET CORRECT BEHAVIOUR THIS IS ONLY FOR DEV PURPOSES
        today: date = date.today() - timedelta(days=1)
        logger.info("Submitting ballot for user %s on %s", user_id, today)

        lottery: Optional[Lottery] = self.lottery_repo.get_by_date(today)
        if not lottery:
            logger.debug("No lottery found for %s, creating new one", today)
            lottery = self.lottery_repo.create_lottery(input_date=today)
            logger.info("Created lottery %s for date %s", lottery.lottery_id, today)

        if lottery is not None and lottery.closed:
            logger.error("Attempt to submit to closed lottery %s", lottery.lottery_id)
            raise HTTPException(
                status_code=400,
                detail="Lottery is already closed for today",
            )

        ballot = self.ballot_repo.create_ballot(user_id=user_id, lottery_id=lottery.lottery_id, expiry_date=today)

        response = BallotResponse.model_validate(ballot)
        logger.info("Ballot submitted: %s for lottery %s (user %s)",
                ballot.ballot_id, lottery.lottery_id, user_id )
        return response

    def list_ballots_by_user(self, user_id : int) -> List[BallotResponse]:
        try:
            ballot_models : List[Ballot] =  self.ballot_repo.list_by_user(user_id=user_id)
            ballot_list = [BallotResponse.model_validate(p) for p in ballot_models]
            if not ballot_list:
                raise ValueError("participant has no registered ballots")
            return ballot_list
        except:
            raise HTTPException(status_code=404, detail="No ballots found for this user")
