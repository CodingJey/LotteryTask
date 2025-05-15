from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic 
from datetime import date
from app.models.ballot import Ballot 
from sqlalchemy.orm import Session 
from app.repositories.interfaces.base_repo_interface import BaseRepositoryInterface

ModelType = TypeVar('ModelType')

class BallotRepositoryInterface(BaseRepositoryInterface[Ballot]):


    @abstractmethod
    def create_ballot(self, user_id: int, lottery_id: int, expiry_date: date) -> Ballot:
        pass

    @abstractmethod
    def get_ballot(self, ballot_id: int) -> Optional[Ballot]: # Often covered by base get
        pass

    @abstractmethod
    def list_by_user(self, user_id: int) -> List[Ballot]:
        pass

    @abstractmethod
    def list_by_lottery(self, lottery_id: int) -> List[Ballot]:
        pass
