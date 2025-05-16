from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from typing import List, Optional
import logging
from app.services.participant_service import ParticipantService
from app.schemas.participant import ( ParticipantCreate, ParticipantResponse )
from app.schemas.ballots import (BallotCreate, BallotResponse)

logger = logging.getLogger("app")


router = APIRouter()

@router.post("/participant",
             response_model=ParticipantResponse,
             status_code=201,
             summary="Create a new participant")
def create_ballot(
    participant_in: ParticipantCreate,
    service: ParticipantService = Depends(ParticipantService),
):
    """
    Registers a new participant. Raises 400 if already exists.
    """
    return service.register_participant(participant_in)

@router.get("/participant",
             response_model=List[ParticipantResponse],
             summary="Get all participants")
def get_participants_list(
    service: ParticipantService = Depends(ParticipantService)
):
    """
    Retrieve all participants.
    """
    participants = service.list_all_participants()
    return participants


@router.get("/participant/{user_id}", 
            response_model=Optional[ParticipantResponse], 
            summary="Get a Participant by its ID")
def get_participant_by_id(
    user_id : int,
    service: ParticipantService = Depends(ParticipantService)
):
    """
    Retrieve participant by id.
    """
    participants = service.get_participant_by_id(user_id=user_id)
    return participants


