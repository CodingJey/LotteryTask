from app.models.winning_ballots import WinningBallot
from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List

from app.services.lottery_service import LotteryService, get_lottery_service
from app.schemas.ballots import (BallotResponse)
from app.schemas.winning_ballot import (WinningBallotResponse)


router = APIRouter()

@router.post("/lottery/close", response_model=WinningBallotResponse)
def close_lottery_and_draw(
    service: LotteryService = Depends(get_lottery_service),
):
    """
    Registers a new ballot. Raises 400 if already exists.
    """
    return service.close_lottery_and_draw()