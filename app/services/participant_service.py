import logging
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from app.repositories.participant_repository import ParticipantRepository, get_participant_repository
from app.db.database import db  

logger = logging.getLogger("app")

class ParticipantService:
    def __init__(self, subscriber_repo: ParticipantRepository):
        self.subscriber_repo = subscriber_repo


def get_participant_service(session: Session = Depends(db.get_db)) -> ParticipantService:
    repo = get_participant_repository(session)
    return ParticipantService(repo)