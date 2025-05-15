import logging
from datetime import date, timedelta
from typing import Optional, List
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
from app.schemas.winning_ballot import(
    WinningBallotResponse
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


    def close_lottery_and_draw(self) -> Optional[WinningBallotResponse]:
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
            raise HTTPException(status_code=418, detail="No lottery found for given date")

        # 3. If it’s already been closed, we do nothing
        if lottery.closed:
            logger.info("Lottery %s (%s) already closed; skipping", lottery.lottery_id, closing_date)
            raise HTTPException(status_code=418, detail=" It’s already been closed")

        # 4. Gather all ballots for that closed date and close any that are not closed correctly
        ballots = self.ballot_repo.list_by_lottery(lottery.lottery_id)
        if not ballots:
            logger.warning(
                "No ballots submitted for lottery %s on %s; marking closed without a winner",
                lottery.lottery_id, closing_date
            )
            self.lottery_repo.mark_as_closed(lottery.lottery_id)
            raise HTTPException(status_code=418, detail="No ballots submitted for lottery, marking closed without a winner")
        # 5. Pick a random winner
        winner_ballot = random.choice(ballots)
        logger.info(
            "Selected winner ballot %s for lottery %s on %s",
            winner_ballot.ballot_id, lottery.lottery_id, closing_date
        )

        # 6. Persist the winning record
        win_record = self.winning_repo.create_winning_ballot(
            lottery_id=lottery.lottery_id,
            ballot_id=winner_ballot.ballot_id,
            winning_date=closing_date,
        )
        logger.info("Winning record created for lottery %s: ballot %s",
                    lottery.lottery_id, winner_ballot.ballot_id)

        # 7. Finally, mark the lottery closed
        self.lottery_repo.mark_as_closed(lottery.lottery_id)
        logger.debug("Lottery %s marked as closed", lottery.lottery_id)

        return win_record

def get_lottery_service(session: Session = Depends(db.get_db)) -> LotteryService:
    logger.debug("Providing WinnerService via DI")
    return LotteryService(session=session)