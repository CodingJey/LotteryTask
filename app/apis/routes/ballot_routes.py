from fastapi import APIRouter, Depends
from typing import List

from app.services.ballot_service import BallotService
from app.schemas.ballots import (BallotResponse, BallotCreate)

router = APIRouter()

@router.post("/ballot/{user_id}", 
             response_model=BallotResponse,
             status_code=201,
             summary="Create a new ballot")
def create_ballot(
    user_id: int,
    service: BallotService = Depends(BallotService),
):
    """
    Registers a new ballot. Raises 400 if already exists.
    """
    return service.create_ballot(user_id=user_id)

@router.post("/ballot", 
             response_model=BallotResponse,
             status_code=201,
             summary="Create a new ballot with a specific expiry date")
def create_ballot_with_expiry_date(
    req : BallotCreate,
    service: BallotService = Depends(BallotService),
):
    """
    Registers a new ballot. Raises 400 if already exists.
    """
    return service.create_ballot_with_date(req)

@router.get("/ballot/{user_id}",
             response_model=List[BallotResponse],
             summary="List of ballots per user")
def list_ballots_by_user(
    user_id: int,
    service: BallotService = Depends(BallotService),
):
    """
    Lists Ballots by UserID. Raises 404 if list is empty.
    """
    
    return service.list_ballots_by_user(user_id=user_id)