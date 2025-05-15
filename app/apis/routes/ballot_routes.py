from app.models.winning_ballots import WinningBallot
from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List

from app.services.ballot_service import BallotService
from app.schemas.ballots import (BallotResponse)
from app.schemas.winning_ballot import (WinningBallotResponse)


router = APIRouter()

@router.post("/ballot/{user_id}", response_model=BallotResponse, status_code=201)
def create_ballot(
    user_id: int,
    service: BallotService = Depends(BallotService),
):
    """
    Registers a new ballot. Raises 400 if already exists.
    """
    return service.create_ballot(user_id=user_id)

@router.get("/ballot", response_model=List[BallotResponse])
def list_ballots_by_user(
    user_id: int,
    service: BallotService = Depends(BallotService),
):
    """
    Lists Ballots by UserID. Raises 404 if list is empty.
    """
    return service.list_ballots_by_user(user_id=user_id)