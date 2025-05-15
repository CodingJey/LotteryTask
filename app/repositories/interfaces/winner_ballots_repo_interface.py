from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar
from datetime import date
from app.models import WinningBallot
from sqlalchemy.orm import Session 
from app.repositories.interfaces.base_repo_interface import BaseRepositoryInterface

ModelType = TypeVar('ModelType')

class WinningBallotRepositoryInterface(BaseRepositoryInterface[WinningBallot]): 
    """Interface for WinningBallot repository operations."""

    @abstractmethod
    def create_winning_ballot(
        self, lottery_id: int, ballot_id: int, winning_date: date
    ) -> WinningBallot:
        """Creates a new winning ballot record."""
        pass

    @abstractmethod
    def get_by_lottery(self, lottery_id: int) -> Optional[WinningBallot]:
        """Gets the winning ballot associated with a specific lottery."""
        pass

    @abstractmethod
    def get_by_ballot(self, ballot_id: int) -> Optional[WinningBallot]:
        """Gets a winning ballot record by the ballot ID."""
        pass

    @abstractmethod
    def get_by_winning_date(self, winning_date: date) -> Optional[WinningBallot]:
        """Gets the winning ballot for a specific date."""
        pass

    @abstractmethod
    def list_winning_ballots(self) -> List[WinningBallot]:
        """Lists all winning ballots."""
        pass