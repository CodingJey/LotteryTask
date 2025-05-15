from app.models.ballot import Ballot
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging 
from typing import List, Optional
from datetime import date
import random
import string 

logger = logging.getLogger("app")

class BallotRepository(BaseRepository[Ballot]):
    def __init__(self, session: Session):
        super().__init__(session, Ballot)

    def _init_ballot(self, user_id: int, lottery_id: int,  expiry_date: date) -> Ballot:
        b = self.model()
        b.user_id = user_id
        b.lottery_id = lottery_id
        b.ballot_number = ''.join(random.choices(string.digits, k=10))
        b.expiry_date = expiry_date
        return b

    def create_ballot(
        self,
        user_id: int,
        lottery_id: int,
        expiry_date: date
    ) -> Ballot:
        """Create and persist a new Ballot."""
        logger.debug(f"Creating Ballot for User={user_id}, Lottery={lottery_id}")
        ballot = self._init_ballot(
            user_id=user_id,
            lottery_id=lottery_id,
            expiry_date=expiry_date
        )
        self.session.add(ballot)
        self.session.commit()
        self.session.refresh(ballot)
        logger.info(f"Created Ballot with ID={ballot.ballot_id}")
        return ballot

    def get_ballot(self, ballot_id: int) -> Optional[Ballot]:
        """Retrieve a ballot by its primary key."""
        return self.get(ballot_id)

    def list_by_user(self, user_id: int) -> List[Ballot]:
        """List ballots belonging to a given user."""
        logger.debug(f"Listing Ballots for User={user_id}")
        stmt = select(Ballot).where(Ballot.user_id == user_id)
        result = self.session.execute(stmt)
        return result.scalars().all()

    def list_by_lottery(self, lottery_id: int) -> List[Ballot]:
        """List ballots for a specific lottery."""
        logger.debug(f"Listing Ballots for Lottery={lottery_id}")
        stmt = select(Ballot).where(Ballot.lottery_id == lottery_id)
        result = self.session.execute(stmt)
        return result.scalars().all()

def get_ballot_repository(session: Session) -> BallotRepository:
    return BallotRepository(session)