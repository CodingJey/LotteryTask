from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List

from app.services.lottery_service import LotteryService, get_lottery_service
from app.schemas.lottery import ( LotteryCreate, ParticipantResponse )
from app.schemas.ballots import (BallotCreate, BallotResponse)

router = APIRouter()

