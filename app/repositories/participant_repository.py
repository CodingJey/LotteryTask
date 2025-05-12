from app.models.participant import Participant
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging 


logger = logging.getLogger("app")

class ParticipantRepository(BaseRepository):
    def __init__(self, session: Session):
        self.session = session
        self.model = Participant

    def does_participant_exist(self, email: str) -> bool:
        result = self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        exists = result.scalars().first() is not None
        return exists

    def create_participant(self, name: str, last_name : str, birth_date : str) -> Participant:
        participant = _init_participant(name, last_name, birth_date)
        self.session.add(participant)
        self.session.commit()
        self.session.refresh(participant)
        return participant

    def _init_participant(self, name: str, last_name : str, birth_date : str) -> Participant:
        participant = self.model()
        participant.name = name
        participant.last_name = last_name
        participant.birth_date
        
        return Participant

def get_participant_repository(session: Session) -> ParticipantRepository:
    return ParticipantRepository(session)