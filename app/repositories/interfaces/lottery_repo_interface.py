from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic 
from datetime import date
from app.models.lottery import Lottery 
from sqlalchemy.orm import Session 
from app.repositories.interfaces.base_repo_interface import BaseRepositoryInterface

ModelType = TypeVar('ModelType')

class LotteryRepositoryInterface(BaseRepositoryInterface[Lottery]):
    """Interface for Lottery repository operations."""

    @abstractmethod
    def create_lottery(self, input_date: date, closed: bool = False) -> Optional[Lottery]:
        """Creates a new lottery."""
        pass

    @abstractmethod
    def get_by_date(self, target_date: date) -> Optional[Lottery]:
        """Fetches a lottery by its specific date."""
        pass

    @abstractmethod
    def get_lottery(self, lottery_id: any) -> Optional[Lottery]: # 'any' for pk type flexibility
        """Retrieves a lottery by its primary key."""
        pass

    @abstractmethod
    def list_lotteries(self) -> List[Lottery]:
        """Lists all lotteries."""
        pass

    @abstractmethod
    def mark_as_closed(self, lottery_id: int) -> Optional[Lottery]:
        """Marks a specified lottery as closed."""
        pass

    @abstractmethod
    def close_lottery_by_date(self, target_date: date) -> Optional[Lottery]:
        """Finds a lottery by date and marks it as closed."""
        pass