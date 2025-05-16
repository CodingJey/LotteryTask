from app.models.winning_ballots import WinningBallot
from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List

from app.services.winner_service import WinnerService
from app.schemas.ballots import (BallotResponse)
from app.schemas.winning_ballot import (WinningBallotResponse)


router = APIRouter()

@router.get("/winner-ballot", 
             response_model=List[WinningBallotResponse],
             summary="Get all winning ballots")
def get_all_winners(
    service: WinnerService = Depends(WinnerService),
):
    """
    Get all winning ballots. 
    """
    return service.list_all_winning_ballots()

@router.get("/winner-ballot/by-date",
             response_model=WinningBallotResponse,
             summary="Get a winner by a given winning date")
def get_winner_by_winning_date(
    winning_date : date,
    service: WinnerService = Depends(WinnerService),
):
    """
    Get a winning ballot by Date. Raises 400 if already exists.
    """
    return service.get_winner_by_winning_date(winning_date)

@router.get("/winner-ballot/{lottery_id}",
             response_model=WinningBallotResponse,
             summary="Get a winner by a given winning lottery ID")
def get_winner_by_lottery_id(
    lottery_id : int,
    service: WinnerService = Depends(WinnerService),
):
    """
    Get a winning lottery by ID. Raises 400 if already exists.
    """
    return service.get_winner_by_lottery_id(lottery_id)