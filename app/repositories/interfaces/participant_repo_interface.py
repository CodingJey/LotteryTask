from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic 
from datetime import date
from app.models.participant import Participant 
from sqlalchemy.orm import Session 
from app.repositories.interfaces.base_repo_interface import BaseRepositoryInterface

ModelType = TypeVar('ModelType')

class ParticipantRepositoryInterface(BaseRepositoryInterface[Participant]): 
    """Interface for Participant repository operations."""

    @abstractmethod
    def create_participant(self, first_name: str, last_name: str, birth_date: date) -> Participant:
        """Creates a new participant."""
        pass

    @abstractmethod
    def get_participant_by_id(self, user_id: int) -> Optional[Participant]:
        """Retrieves a participant by their ID."""
        pass

    @abstractmethod
    def get_by_first_name(self, first_name: str) -> Optional[Participant]:
        """Fetches a participant by their first name."""
        pass

    @abstractmethod
    def list_participants(self) -> List[Participant]:
        """Lists all participants."""
        pass