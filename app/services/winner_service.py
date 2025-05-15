import logging
from datetime import date
from typing import Optional, List
from app.db.database import db 

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import db 
from app.repositories.winner_ballots_repository import (
    WinningBallotRepository,
    get_winning_ballot_repository,
)
from app.models.winning_ballots import WinningBallot
from app.schemas.winning_ballot import WinningBallotResponse
from app.repositories.winner_ballots_repository import (
     get_winning_ballot_repository,
)
logger = logging.getLogger(__name__)

class WinnerService:
    def __init__(
        self,
        session: Session = Depends(db.get_db),
    ):
        self.winning_repo = get_winning_ballot_repository(session=session)
        logger.debug("Initialized WinnerService")

    def record_new_winner(
        self, lottery_id: int, ballot_id: int, winning_date: date
    ) -> WinningBallotResponse:
        """
        Creates and persists a new WinningBallot record.
        This is called by LotteryService after a winner is drawn.
        """
        logger.info(
            f"Recording new winner for LotteryID={lottery_id}, BallotID={ballot_id}, WinningDate={winning_date}"
        )

        win_record_model = self.winning_repo.create_winning_ballot(
            lottery_id=lottery_id, ballot_id=ballot_id, winning_date=winning_date
        )
        # The original close_lottery_and_draw returned the model instance,
        # but service methods should ideally return Pydantic schemas.
        logger.info(
            f"Successfully created WinningBallot (ID: {win_record_model.lottery_id}) for LotteryID={lottery_id}"
        )
        return WinningBallotResponse.model_validate(win_record_model)

    def get_winner_by_winning_date(self, winning_date: date) -> WinningBallotResponse:
        """
        Retrieves the winning ballot for a specific winning date.
        (Moved from LotteryService)
        """
        logger.info(f"Retrieving winner for date {winning_date}")
        win_model: Optional[WinningBallot] = self.winning_repo.get_by_winning_date(winning_date)
        if not win_model:
            logger.warning(f"No winning record found for date {winning_date}")
            raise HTTPException(
                status_code=404,
                detail="No winner found for that date",
            )
        logger.info(
            f"Found winning record (WinningBallotID: {win_model.lottery_id}) for date {winning_date}"
        )
        return WinningBallotResponse.model_validate(win_model)

    def list_all_winning_ballots(self) -> List[WinningBallotResponse]:
        """
        Retrieves a list of all winning ballots with their details.

        Returns:
            A list of winning ballot details. Returns an empty list if no winning ballots are found.
        
        Raises:
            HTTPException: If an unexpected error occurs during retrieval (status 500).
        """
        logger.info("Attempting to retrieve all winning ballots.")
        try:
            winning_ballots_models: List[WinningBallot] = self.winning_repo.list_winning_ballots()
            
            response_list = [ WinningBallotResponse.model_validate(wb_model) for wb_model in winning_ballots_models ]
            
            logger.info(f"Successfully retrieved {len(response_list)} winning ballots.")
            return response_list
        except Exception as e:
            logger.error(
                "Error during listing all winning ballots: %s", str(e), exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while retrieving winning ballots."
            )

def get_winner_service(session: Session = Depends(db.get_db)) -> WinnerService:
    logger.debug("Providing WinnerService via DI")
    return WinnerService(session=session)