import logging
from typing import Optional, List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import db 
from app.models.participant import Participant
from app.repositories.participant_repository import (
    ParticipantRepository, get_participant_repository,
)
from app.repositories.ballot_repository import (BallotRepository, get_ballot_repository )
from app.schemas.participant import (
    ParticipantCreate, ParticipantResponse,
)

logger = logging.getLogger("app.participant_service")
logger.setLevel(logging.INFO)

class ParticipantService:
    """
    Service for managing lottery participants.
    """
    def __init__(
        self,
        session: Session = Depends(db.get_db)
    ) -> None:
        """
        Initializes the ParticipantService.

        Args:
            session: The database session.
        """
        self.ballot_repo : BallotRepository = get_ballot_repository(session=session)
        self.participant_repo: ParticipantRepository = get_participant_repository(session=session)
        logger.debug("Initialized ParticipantService with ParticipantRepository: %s", self.participant_repo)

    def register_participant(
        self, request: ParticipantCreate
    ) -> ParticipantResponse:
        """
        Registers a new lottery participant.

        Checks if a participant with the same first name already exists.
        If a participant exists, raises an HTTPException.
        Otherwise, creates the participant and returns their details.

        Args:
            request: The participant creation request data.

        Returns:
            The created participant's details.

        Raises:
            HTTPException: If a participant with the same first name already exists (status 400)
                           or if an unexpected error occurs during creation (status 500).
        """
        logger.info("Attempting to register participant: %s %s", request.first_name, request.last_name)
        
        # Check if a participant with the given first name already exists
        existing_participant: Optional[Participant] = self.participant_repo.get_by_first_name(
            first_name=request.first_name
        )

        if existing_participant:
            logger.warning(
                "Registration failed: participant with first name '%s' already exists. Requested for: %s %s, DOB: %s",
                request.first_name, request.first_name, request.last_name, request.birth_date
            )
            raise HTTPException(
                status_code=400,  # Bad Request
                detail=f"Participant with first name '{request.first_name}' already exists."
            )

        try:
            # Create the new participant
            new_participant_model = self.participant_repo.create_participant(
                first_name=request.first_name,
                last_name=request.last_name,
                birth_date=request.birth_date
            )
            # Validate and return the response
            response = ParticipantResponse.model_validate(new_participant_model)
            logger.info("Participant created successfully: UserID %s, Name: %s %s",
                        response.user_id, response.first_name, response.last_name)
            return response
        except Exception as e:
            logger.error(
                "Error during participant creation for %s %s: %s",
                request.first_name, request.last_name, str(e), exc_info=True
            )
            raise HTTPException(
                status_code=500,  # Internal Server Error
                detail="An unexpected error occurred while creating the participant."
            )

    def list_all_participants(self) -> List[ParticipantResponse]:
        """
        Retrieves a list of all registered participants.

        Returns:
            A list of participant details. Returns an empty list if no participants are found.
        
        Raises:
            HTTPException: If an unexpected error occurs during retrieval (status 500).
        """
        logger.info("Attempting to retrieve all participants.")
        try:
            participants_models: List[Participant] = self.participant_repo.list_participants()
            
            # Convert list of ORM models to list of Pydantic response models
            response_list = [ParticipantResponse.model_validate(p) for p in participants_models]
            
            logger.info(f"Successfully retrieved {len(response_list)} participants.")
            return response_list
        except Exception as e:
            logger.error(
                "Error during listing all participants: %s", str(e), exc_info=True
            )
            # It's generally good practice to not expose raw error details to the client
            # unless it's a development environment or specific debugging need.
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while retrieving participants."
            )

def get_participant_service(
    session: Session = Depends(db.get_db)
) -> ParticipantService:
    """
    Dependency injector for ParticipantService.

    Args:
        session: The database session.
    Returns:
        An instance of ParticipantService.
    """
    logger.debug("Providing ParticipantService via DI")
    return ParticipantService(session=session)
