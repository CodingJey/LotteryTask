import logging
from datetime import date, timedelta
from typing import Optional
import random
from app.db.database import db  
from app.schemas.ballots import BallotResponse
from app.schemas.participant import ParticipantResponse
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from app.repositories.participant_repository import (
    ParticipantRepository, get_participant_repository,
)
from app.repositories.lottery_repository import (
    LotteryRepository, get_lottery_repository,
)
from app.repositories.ballot_repository import (
    BallotRepository, get_ballot_repository,
)
from app.repositories.winner_ballots_repository import (
    WinningBallotRepository, get_winning_ballot_repository,
)
from app.models.ballot import (
  Ballot, 
)
from app.models.lottery import (
    Lottery,
)
from app.models.winning_ballots import (
  WinningBallot,
)
from app.models.participant import (
    Participant,
)
from app.schemas.participant import(
    ParticipantResponse, ParticipantCreate
)

logger = logging.getLogger("app.lottery")
logger.setLevel(logging.INFO)


class LotteryService:
    def __init__(
        self,
        session: Session = Depends(db.get_db)
    ) -> None:
        self.participant_repo = get_participant_repository(session=session)
        self.lottery_repo = get_lottery_repository(session=session)
        self.ballot_repo = get_ballot_repository(session=session)
        self.winning_repo = get_winning_ballot_repository(session=session)
        logger.debug("Initialized LotteryService with repos: %s, %s, %s, %s",
                     self.participant_repo, self.lottery_repo, self.ballot_repo, self.winning_repo)

    def register_participant(
        self, request: ParticipantCreate
    ) -> ParticipantResponse:
        """
        Registers a new lottery participant.
        Raises HTTPException if a participant with the same first name already exists.
        """
        logger.info("Attempting to register participant: %s %s", request.first_name, request.last_name)
        existing_participant: Optional[Participant] = self.participant_repo.get_by_first_name(first_name=request.first_name)

        if existing_participant:
            # Log with more details if possible, e.g., existing_participant.UserID if available
            logger.warning(
                "Registration failed: participant with name '%s' already exists. Requested for: %s %s",
                request.first_name, request.last_name, request.birth_date
            )
            # If participant exists, raise HTTPException and stop execution
            raise HTTPException(
                status_code=400, 
                detail=f"Participant with name '{request.first_name}' already exists."
            )

        try:
            new_participant_model = self.participant_repo.create_participant(
                first_name=request.first_name,
                last_name=request.last_name,
                birth_date=request.birth_date
            )
            response = ParticipantResponse.model_validate(new_participant_model)
            logger.info("Participant created successfully: UserID %s, Name: %s %s",
                        response.user_id, response.first_name, response.last_name)
            return response
        except Exception as e: 
            logger.error(
                "Error during participant creation for %s %s: %s",
                request.first_name, request.last_name, str(e), exc_info=True 
            )
            raise HTTPException(
                status_code=500,  # Internal Server Error
                detail="An unexpected error occurred while creating the participant."
            )
    
    def submit_ballot(self, user_id: int) -> BallotResponse:
        """
        Submits a new ballot for today's lottery; creates the lottery if missing.
        """
        today: date = date.today()
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

        ballot = self.ballot_repo.create_ballot(user_id=user_id, lottery_id=lottery.lottery_id, ExpiryDate=today)

        response = BallotResponse.model_validate(ballot)
        logger.info("Ballot submitted: %s for lottery %s (user %s)",
                ballot.ballot_id, lottery.lottery_id, user_id, )
        return response

    def close_and_draw(self) -> Optional[WinningBallot]:
        """
        Closes *yesterday’s* lottery (i.e., the one whose date was “today - 1 day”)
        and selects a random winning ballot. Returns the winning record, or None if:
          - no lottery existed for yesterday
          - it was already closed
          - there were no ballots
        """

        # 1. Calculate the date whose lottery we should now close:
        closing_date = date.today() - timedelta(days=1)
        logger.info("Running close_and_draw for lottery date %s", closing_date)

        # 2. Fetch the lottery for that day
        lottery = self.lottery_repo.get_by_date(closing_date)
        if lottery is None:
            logger.info("No lottery found for %s; skipping close", closing_date)
            return None

        # 3. If it’s already been closed, we do nothing
        if lottery.closed:
            logger.info("Lottery %s (%s) already closed; skipping", lottery.lottery_id, closing_date)
            return None

        # 4. Gather all ballots for that closed date
        ballots = self.ballot_repo.list_by_lottery(lottery.lottery_id)
        if not ballots:
            logger.warning(
                "No ballots submitted for lottery %s on %s; marking closed without a winner",
                lottery.lottery_id, closing_date
            )
            self.lottery_repo.mark_closed(lottery.lottery_id)
            return None

        # 5. Pick a random winner
        winner_ballot = random.choice(ballots)
        logger.info(
            "Selected winner ballot %s for lottery %s on %s",
            winner_ballot.ballot_id, lottery.lottery_id, closing_date
        )

        # 6. Persist the winning record
        win_record = self.winning_repo.create(
            lottery_id=lottery.lottery_id,
            ballot_id=winner_ballot.ballot_id,
            winning_date=closing_date,
        )
        logger.info("Winning record created for lottery %s: ballot %s",
                    lottery.lottery_id, winner_ballot.ballot_id)

        # 7. Finally, mark the lottery closed
        self.lottery_repo.mark_closed(lottery.lottery_id)
        logger.debug("Lottery %s marked as closed", lottery.lottery_id)

        return win_record
        
    def get_winner_by_date(self, query_date: date) :
        """
        Retrieves the winning ballot for a specific lottery date.
        Raises 404 if not found.
        """
        # logger.info("Retrieving winner for date %s", query_date)
        # win: Optional[WinningBallot] = self.winning_repo.get_by_date(query_date)
        # if not win:
        #     logger.error("No winning record found for %s", query_date)
        #     raise HTTPException(status_code=404, detail="No winner found for that date")
        # return win
        return None

def get_lottery_service(
    session: Session = Depends(db.get_db)
   ) -> LotteryService:
    logger.debug("Providing LotteryService via DI")
    return LotteryService(session=session)