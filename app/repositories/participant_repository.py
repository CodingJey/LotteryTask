from app.models.participant import Participant
from app.repositories.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging 
from typing import List, Optional
from datetime import date

logger = logging.getLogger("app")

class ParticipantRepository(BaseRepository[Participant]):
    def __init__(self, session: Session):
        super().__init__(session, Participant)

    def create_participant(self, first_name: str, last_name: str, birth_date: date) -> Participant:
        """Create and persist a new Participant."""
        logger.debug(f"Creating Participant: {first_name} {last_name}")
        participant = self._init_participant(first_name=first_name, last_name=last_name, birth_date=birth_date)
        self.session.add(participant)
        self.session.commit()
        self.session.refresh(participant)
        logger.info(f"Created Participant with ID={participant.user_id}")
        return participant

    def get_participant(self, user_id: int) -> Optional[Participant]:
        """Retrieve a Participant by its primary key."""
        return self.get(user_id)

    def get_by_first_name(self, first_name: str) -> Optional[Participant]:
        """Fetch participants filtering by first name."""
        logger.debug(f"Fetching Participants by FirstName={first_name}")
        stmt = select(Participant).where(Participant.first_name == first_name)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def list_participants(self) -> List[Participant]:
        """List all participants."""
        return self.list_all()

    def _init_participant(self, first_name: str, last_name: str, birth_date: date) -> Participant:
        p = self.model()
        p.first_name = first_name
        p.last_name = last_name
        p.birth_date = birth_date
        return p


def get_participant_repository(session: Session) -> ParticipantRepository:
    return ParticipantRepository(session)