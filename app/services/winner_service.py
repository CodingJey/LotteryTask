import logging
from datetime import date
from typing import Optional, List
from fastapi import Depends, HTTPException
from app.repositories.interfaces.winner_ballots_repo_interface import WinningBallotRepositoryInterface
from app.models.winning_ballots import WinningBallot
from app.schemas.winning_ballot import WinningBallotResponse
from app.repositories.winner_ballots_repository import (
     get_winning_ballot_repository_provider,
)
from app.middleware.exceptions.winner_service_exceptions import (
    WinnerServiceError,
    WinnerNotFoundError,
    WinnerListingError,
)

logger = logging.getLogger("app")

class WinnerService:
    def __init__(
        self,
        winning_repo: WinningBallotRepositoryInterface = Depends(get_winning_ballot_repository_provider)
    ):
        self.winning_repo = winning_repo
        logger.debug("Initialized WinnerService")


    def get_winner_by_winning_date(self, winning_date: date) -> WinningBallotResponse:
        """
        Retrieves the winning ballot for a specific winning date.

        Raises:
            WinnerNotFoundError: If no winning ballot is found for the given date.
            WinnerServiceError: For other unexpected errors during retrieval.
        """
        logger.info(f"Attempting to retrieve winner for date {winning_date}")
        try:
            win_model: Optional[WinningBallot] = self.winning_repo.get_by_winning_date(winning_date)
        except Exception as e:
            logger.error(f"Repository error while fetching winner for date {winning_date}: {str(e)}", exc_info=True)
            raise WinnerServiceError(message=f"Failed to retrieve winner for date {winning_date} due to repository error: {str(e)}", operation="get_winner_by_winning_date")

        if not win_model:
            logger.warning(f"No winning record found for date {winning_date}")
            raise WinnerNotFoundError(identifier=winning_date, operation="get_winner_by_winning_date")

        logger.info(
            f"Found winning record (LotteryID: {win_model.lottery_id}, BallotID: {win_model.ballot_id}) for date {winning_date}"
        )
        return WinningBallotResponse.model_validate(win_model)

    def list_all_winning_ballots(self) -> List[WinningBallotResponse]:
        """
        Retrieves a list of all winning ballots with their details.
        Returns an empty list if no winning ballots are found (does not raise error for empty list).

        Raises:
            WinnerListingError: If an unexpected error occurs during retrieval from the repository.
        """
        logger.info("Attempting to retrieve all winning ballots.")
        try:
            winning_ballots_models: List[WinningBallot] = self.winning_repo.list_winning_ballots()
            
            response_list = [
                WinningBallotResponse.model_validate(wb_model) for wb_model in winning_ballots_models
            ]
            
            logger.info(f"Successfully retrieved {len(response_list)} winning ballots.")
            return response_list
        except Exception as e:
            logger.error(
                f"Repository error during listing all winning ballots: {str(e)}", exc_info=True
            )
            raise WinnerListingError(reason=str(e))

    def get_winner_by_lottery_id(self, lottery_id: int) -> Optional[WinningBallotResponse]:
        """
        Retrieves the winning ballot for a specific lottery ID.
        Returns None if not found, or raises WinnerNotFoundError if preferred.

        Raises:
            WinnerNotFoundError: If no winning ballot is found for the given lottery ID.
            WinnerServiceError: For other unexpected errors during retrieval.
        """
        logger.info(f"Attempting to retrieve winner for LotteryID={lottery_id}")
        try:
            win_model: Optional[WinningBallot] = self.winning_repo.get_by_lottery(lottery_id)
        except AttributeError:
             logger.error(f"Repository method 'get_by_lottery_id' not found. Cannot fetch winner by lottery ID.")
             raise WinnerServiceError(message="Underlying repository does not support fetching winner by lottery ID.", operation="get_winner_by_lottery_id")
        except Exception as e:
            logger.error(f"Repository error while fetching winner for LotteryID={lottery_id}: {str(e)}", exc_info=True)
            raise WinnerServiceError(message=f"Failed to retrieve winner for LotteryID={lottery_id} due to repository error: {str(e)}", operation="get_winner_by_lottery_id")

        if not win_model:
            logger.warning(f"No winning record found for LotteryID={lottery_id}")
            raise WinnerNotFoundError(identifier=lottery_id, operation="get_winner_by_lottery_id")
        
        logger.info(
            f"Found winning record (BallotID: {win_model.ballot_id}) for LotteryID={lottery_id}"
        )
        return WinningBallotResponse.model_validate(win_model)
            