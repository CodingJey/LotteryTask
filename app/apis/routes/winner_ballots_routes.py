from app.models.winning_ballots import WinningBallot
from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List

from app.services.winner_service import WinnerService
from app.schemas.ballots import (BallotResponse)
from app.schemas.winning_ballot import (WinningBallotResponse)


router = APIRouter()

@router.get("/winner-ballot", response_model=List[WinningBallotResponse])
def get_all_winners(
    service: WinnerService = Depends(WinnerService),
):
    """
    Registers a new ballot. Raises 400 if already exists.
    """
    return service.list_all_winning_ballots()

@router.get("/winner-ballot", response_model=WinningBallotResponse)
def get_winner_by_winning_date(
    winning_date : date,
    service: WinnerService = Depends(WinnerService),
):
    """
    Registers a new ballot. Raises 400 if already exists.
    """
    return service.get_winner_by_winning_date(winning_date)
