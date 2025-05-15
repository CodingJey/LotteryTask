from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List, Optional

from app.services.participant_service import ParticipantService, get_participant_service
from app.schemas.participant import ( ParticipantCreate, ParticipantResponse )
from app.schemas.ballots import (BallotCreate, BallotResponse)

router = APIRouter()

@router.post("/participant", response_model=ParticipantResponse, status_code=201)
def register_participant(
    participant_in: ParticipantCreate,
    service: ParticipantService = Depends(get_participant_service),
):
    """
    Registers a new participant. Raises 400 if already exists.
    """
    return service.register_participant(participant_in)

@router.get("/participant", response_model=List[ParticipantResponse])
def get_participants_list(
    service: ParticipantService = Depends(get_participant_service)
):
    """
    Retrieve all participants.
    """
    participants = service.list_all_participants()
    return participants


@router.get("/participant/{user_id}", response_model=Optional[ParticipantResponse])
def get_participant_by_id(
    user_id : int,
    service: ParticipantService = Depends(get_participant_service)
):
    """
    Retrieve participant by id.
    """
    participants = service.get_participant_by_id(user_id=user_id)
    return participants


