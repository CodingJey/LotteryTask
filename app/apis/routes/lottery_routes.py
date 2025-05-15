from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List

from app.services.lottery_service import LotteryService, get_lottery_service
from app.schemas.lottery import (  LotteryResponse )
from app.schemas.ballots import (BallotCreate, BallotResponse)

router = APIRouter()

@router.post("/ballot/{user_id}", response_model=BallotResponse, status_code=201)
def create_ballot(
    user_id: int,
    service: LotteryService = Depends(get_lottery_service),
):
    """
    Registers a new ballot. Raises 400 if already exists.
    """
    return service.create_ballot(user_id=user_id)