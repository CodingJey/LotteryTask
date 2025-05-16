import logging
from typing import Optional, List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import db 
from app.models.participant import Participant
from app.repositories.participant_repository import ( get_participant_repository_provider)
from app.repositories.ballot_repository import ( get_ballot_repository_provider)
from app.repositories.interfaces.ballot_repo_interface import BallotRepositoryInterface
from app.repositories.interfaces.participant_repo_interface import ParticipantRepositoryInterface
from app.schemas.participant import (
    ParticipantCreate, ParticipantResponse,
)
from app.middleware.exceptions.participant_service_exceptions import (
    ParticipantServiceError,
    ParticipantNotFoundError,
    ParticipantAlreadyExistsError,
    ParticipantCreationError,
    ParticipantListingError
)

logger = logging.getLogger("app")

class ParticipantService:
    """
    Service for managing lottery participants.
    """
    def __init__(
        self,
        ballot_repo: BallotRepositoryInterface = Depends(get_ballot_repository_provider),
        participant_repo: ParticipantRepositoryInterface = Depends(get_participant_repository_provider),
        ) -> None:
        """
        Initializes the ParticipantService.
        """
        self.ballot_repo : BallotRepositoryInterface = ballot_repo
        self.participant_repo: ParticipantRepositoryInterface = participant_repo
        logger.debug("Initialized ParticipantService with ParticipantRepository: %s", self.participant_repo)

    def register_participant(
        self, request: ParticipantCreate
    ) -> ParticipantResponse:
        """
        Registers a new lottery participant.

        Args:
            request: The participant creation request data.

        Returns:
            The created participant's details.

        Raises:
            ParticipantAlreadyExistsError: If a participant with the same first name already exists.
            ParticipantCreationError: If an unexpected error occurs during creation.
        """
        logger.info("Attempting to register participant: %s %s", request.first_name, request.last_name)

        try:
            existing_participant: Optional[Participant] = self.participant_repo.get_by_first_name(
                first_name=request.first_name
            )

            if existing_participant:
                logger.warning(
                    "Registration failed: participant with first name '%s' already exists. Requested for: %s %s, DOB: %s",
                    request.first_name, request.first_name, request.last_name, request.birth_date
                )
                raise ParticipantAlreadyExistsError(
                    identifier_field="first name",
                    identifier_value=request.first_name
                )
        except ParticipantAlreadyExistsError:
            raise # Re-raise the specific error
        except Exception as e:
            logger.error(
                "Error during pre-check for participant %s %s: %s",
                request.first_name, request.last_name, str(e), exc_info=True
            )
            raise ParticipantServiceError(
                message=f"Failed during existence check for participant {request.first_name}: {str(e)}",
                operation="register_participant_check"
            )

        try:
            new_participant_model = self.participant_repo.create_participant(
                first_name=request.first_name,
                last_name=request.last_name,
                birth_date=request.birth_date
            )
            if new_participant_model is None: # Should be handled by repo raising error
                raise ParticipantCreationError(
                    request.first_name, request.last_name, "Repository returned None."
                )

            response = ParticipantResponse.model_validate(new_participant_model)
            logger.info("Participant created successfully: UserID %s, Name: %s %s",
                        response.user_id, response.first_name, response.last_name)
            return response
        except Exception as e: 
            logger.error(
                "Error during participant creation for %s %s: %s",
                request.first_name, request.last_name, str(e), exc_info=True
            )
            raise ParticipantCreationError(
                request.first_name, request.last_name, reason=str(e)
            )

    def list_all_participants(self) -> List[ParticipantResponse]:
        """
        Retrieves a list of all registered participants.

        Returns:
            A list of participant details. Returns an empty list if no participants are found.
        
        Raises:
            ParticipantListingError: If an unexpected error occurs during retrieval.
        """
        logger.info("Attempting to retrieve all participants.")
        try:
            participants_models: List[Participant] = self.participant_repo.list_participants()
            
            response_list = [ParticipantResponse.model_validate(p) for p in participants_models]
            
            logger.info(f"Successfully retrieved {len(response_list)} participants.")
            return response_list
        except Exception as e:
            logger.error(
                "Error during listing all participants: %s", str(e), exc_info=True
            )
            raise ParticipantListingError(reason=str(e))

    def get_participant_by_id(self, user_id: int) -> ParticipantResponse:
        """
        Retrieves a participant by their unique ID.

        Args:
            user_id: The ID of the participant to retrieve.

        Returns:
            The participant's details.
        
        Raises:
            ParticipantNotFoundError: If no participant is found with the given ID.
            ParticipantServiceError: For other unexpected errors during retrieval.
        """
        logger.info(f"Attempting to retrieve participant by ID: {user_id}")
        try:
            participant_model: Optional[Participant] = self.participant_repo.get_participant_by_id(user_id=user_id)
            
            if participant_model is None:
                logger.warning(f"Participant with ID {user_id} not found.")
                raise ParticipantNotFoundError(identifier=user_id)

            response = ParticipantResponse.model_validate(participant_model)
            logger.info(f"Successfully retrieved participant ID {user_id}: {response.first_name} {response.last_name}")
            return response
        except ParticipantNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving participant by ID {user_id}: {str(e)}", exc_info=True
            )
            raise ParticipantServiceError(
                message=f"An unexpected error occurred while retrieving participant ID {user_id}: {str(e)}",
                operation="get_participant_by_id"
            )