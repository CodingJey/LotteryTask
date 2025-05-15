from app.models.winning_ballots import WinningBallot
from app.repositories.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging 
from typing import Optional, List
from datetime import date 

logger = logging.getLogger("app")


class WinningBallotRepository(BaseRepository[WinningBallot]):
    def __init__(self, session: Session):
        super().__init__(session, WinningBallot)

    def create_winning_ballot(
        self,
        lottery_id: int,
        ballot_id: int,
        winning_date: date
    ) -> WinningBallot:
        """Create and persist a WinningBallot entry."""
        logger.debug(f"Recording winning ballot Lottery={lottery_id}, Ballot={ballot_id}")
        winning = self._init_winning_ballot(
            lottery_id=lottery_id,
            ballot_id=ballot_id,
            winning_date=winning_date
        )
        self.session.add(winning)
        self.session.commit()
        self.session.refresh(winning)
        logger.info(f"Created WinningBallot for LotteryID={lottery_id}")
        return winning

    def get_by_lottery(self, lottery_id: int) -> Optional[WinningBallot]:
        """Get the winning ballot for a lottery (one-to-one)."""
        logger.debug(f"Fetching WinningBallot for Lottery={lottery_id}")
        stmt = select(WinningBallot).where(WinningBallot.lottery_id == lottery_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_ballot(self, ballot_id: int) -> Optional[WinningBallot]:
        """Fetch winning entry by ballot."""
        logger.debug(f"Fetching WinningBallot for Ballot={ballot_id}")
        stmt = select(WinningBallot).where(WinningBallot.ballot_id == ballot_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def list_winning_ballots(self) -> List[WinningBallot]:
        """List all winning ballots."""
        return self.list_all()

    def _init_winning_ballot(self, lottery_id: int, ballot_id: int, winning_date: date) -> WinningBallot:
        w = self.model()
        w.lottery_id = lottery_id
        w.ballot_id = ballot_id
        w.winning_date = winning_date
        return w

    
def get_winning_ballot_repository(session: Session) -> WinningBallotRepository:
    return WinningBallotRepository(session)