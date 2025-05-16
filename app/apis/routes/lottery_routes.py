from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List, Optional

from app.services.lottery_service import LotteryService
from app.schemas.ballots import (BallotResponse)
from app.schemas.winning_ballot import (WinningBallotResponse)
from app.schemas.lottery import LotteryResponse,CreateLotteryRequest
from app.services.lottery_service import LotteryAlreadyExistsError,LotteryServiceError, LotteryNotFoundError
import logging 

logger = logging.getLogger("app")

router = APIRouter()

@router.post("/lottery",
             response_model=LotteryResponse,
             status_code=201,
             summary="Create a new lottery")
def create_lottery(
    payload: CreateLotteryRequest,
    service: LotteryService = Depends(LotteryService),
):
    """
    Creates a new lottery for the specified date.
    - `target_date`: The date for which the lottery is to be created.
    - `closed`: (Optional) Whether the lottery should be created in a closed state. Defaults to false.

    Raises:
    - `409 Conflict`: If a lottery for the given date already exists.
    - `400 Bad Request`: If there's an issue with creating the lottery (e.g., repository error).
    """
    try:
        logger.info(f"API: Attempting to create lottery for date: {payload.target_date}")
        lottery = service.create_lottery(target_date=payload.target_date)
        return lottery
    except LotteryAlreadyExistsError as e:
        logger.warning(f"API Error: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except LotteryServiceError as e: # Catch generic service errors
        logger.error(f"API Error: Failed to create lottery - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/lottery/close",
             response_model=WinningBallotResponse,
             summary="Close lottery and Draw Winner Ballot")
def close_lottery_and_draw(
    service: LotteryService = Depends(LotteryService),
):
    """
    Closes lottery and Draws winner. Raises 400 if already exists.
    """
    return service.close_lottery_and_draw()

@router.get("/lottery",
             response_model=List[LotteryResponse],
             summary="List all lotteries")
def list_all_lotteries(
    service: LotteryService = Depends(LotteryService),
):
    """
    Retrieves a list of all lotteries.
    """
    logger.debug("API: Fetching all lotteries.")
    return service.get_all_lotteries()

@router.get("/lottery/open",
             response_model=List[LotteryResponse],
             summary="List all open lotteries")
def list_open_lotteries(
    service: LotteryService = Depends(LotteryService),
):
    """
    Retrieves a list of all lotteries that are currently open (not closed).
    """
    logger.debug("API: Fetching all open lotteries.")
    return service.get_open_lotteries()

@router.get("/lottery/active-today",
            response_model=Optional[LotteryResponse],
            summary="Get today's active lottery")
def get_todays_active_lottery(
    service: LotteryService = Depends(LotteryService),
):
    """
    Retrieves the active (open) lottery for the current date.
    Returns the lottery details if found and open, otherwise returns null/None.
    """
    logger.debug("API: Fetching active lottery for today.")
    lottery = service.get_active_lottery_for_today()
    if not lottery:
        logger.info("API: No active lottery found for today.")
    return lottery

@router.get("/lottery/{lottery_id}",
             response_model=LotteryResponse,
             summary="Get a lottery by its ID")
def get_lottery(
    lottery_id: int,
    service: LotteryService = Depends(LotteryService),
):
    """
    Retrieves a specific lottery by its unique ID.

    Raises:
    - `404 Not Found`: If the lottery with the given ID does not exist.
    """
    logger.debug(f"API: Fetching lottery by ID: {lottery_id}")
    lottery = service.get_lottery(lottery_id)
    return lottery

@router.get("/lottery/by-date/{target_date}",
             response_model=LotteryResponse,
             summary="Get a lottery by its date")
def get_lottery_by_date(
    target_date: date,
    service: LotteryService = Depends(LotteryService)
):
    """
    Retrieves a specific lottery by its date.

    Raises:
    - `404 Not Found`: If no lottery exists for the given date.
    """
    logger.debug(f"API: Fetching lottery by date: {target_date}")
    lottery = service.get_lottery_by_target_date(target_date)
    return lottery

