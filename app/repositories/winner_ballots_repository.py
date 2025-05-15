from app.models.winning_ballots import WinningBallot
from app.repositories.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError 
import logging 
from typing import Optional, List
from datetime import date 
import random
from app.db.database import db  
from fastapi import Depends
from app.repositories.interfaces.winner_ballots_repo_interface import WinningBallotRepositoryInterface

logger = logging.getLogger("app")


class WinningBallotRepository(BaseRepository[WinningBallot], WinningBallotRepositoryInterface):
    def __init__(self, session: Session):
        super().__init__(session, WinningBallot)

    def _init_winning_ballot(self, lottery_id: int, ballot_id: int, winning_date: date) -> WinningBallot:
        w = self.model()
        w.lottery_id = lottery_id
        w.ballot_id = ballot_id
        w.winning_date = winning_date
        w.winning_amount = random.randint(2, 100)
        return w

    def create_winning_ballot(
        self, lottery_id: int, ballot_id: int, winning_date: date
    ) -> WinningBallot:
        """
        Create and persist a WinningBallot entry with transaction handling.
        Rolls back on error and re-raises the exception.
        """
        logger.debug(
            f"Attempting to create WinningBallot for LotteryID={lottery_id}, "
            f"BallotID={ballot_id}, WinningDate={winning_date}"
        )
        # Initialize the model instance
        winning_ballot_model = self._init_winning_ballot(
            lottery_id=lottery_id, ballot_id=ballot_id, winning_date=winning_date
        )

        try:
            self.session.add(winning_ballot_model)
            self.session.commit()
            self.session.refresh(winning_ballot_model)
            logger.info(
                f"Successfully created WinningBallot (ID: {winning_ballot_model.lottery_id}) "
                f"for LotteryID={lottery_id}"
            )
            return winning_ballot_model
        except SQLAlchemyError as e: 
            self.session.rollback()
            logger.error(
                f"SQLAlchemyError: Failed to create WinningBallot for LotteryID={lottery_id}. Rolling back. Error: {e}",
                exc_info=True,
            )
            raise # Re-raise the caught SQLAlchemyError
        except Exception as e: # Catch any other unexpected errors
            self.session.rollback()
            logger.error(
                f"UnexpectedError: Failed to create WinningBallot for LotteryID={lottery_id}. Rolling back. Error: {e}",
                exc_info=True,
            )
            raise 

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

    def get_by_winning_date(self, winning_date: date) -> Optional[WinningBallot]:
        """Get the winning ballot for a specific winning date."""
        logger.debug(f"Fetching WinningBallot for WinningDate={winning_date}")
        stmt = select(WinningBallot).where(WinningBallot.winning_date == winning_date)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def list_winning_ballots(self) -> List[WinningBallot]:
        """List all winning ballots."""
        return self.list_all()
    
def get_winning_ballot_repository_provider(
    session: Session = Depends(db.get_db)
) -> WinningBallotRepositoryInterface:
    return WinningBallotRepository(session=session)
