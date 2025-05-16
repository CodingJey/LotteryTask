from typing import Union
from .base_exceptions import ServiceError

class ParticipantServiceError(ServiceError):
    """Base class for exceptions raised by the ParticipantService."""
    def __init__(self, message: str, operation: str = "unknown"):
        self.operation = operation
        super().__init__(f"ParticipantService error during {operation}: {message}")

# --- Specific Participant Service Exceptions ---
class ParticipantNotFoundError(ParticipantServiceError):
    """Raised when a participant is not found for a given identifier."""
    def __init__(self, identifier: Union[int, str], operation: str = "retrieval"): # Identifier can be ID or name
        self.identifier = identifier
        super().__init__(f"Participant with identifier '{identifier}' not found.", operation)

class ParticipantAlreadyExistsError(ParticipantServiceError):
    """Raised when attempting to register a participant that already exists (e.g., by name or email)."""
    def __init__(self, identifier_field: str, identifier_value: str, operation: str = "registration"):
        self.identifier_field = identifier_field
        self.identifier_value = identifier_value
        super().__init__(f"Participant with {identifier_field} '{identifier_value}' already exists.", operation)

class ParticipantCreationError(ParticipantServiceError):
    """Raised when there's an issue creating a participant record in the repository."""
    def __init__(self, first_name: str, last_name: str, reason: str = "Could not create participant in repository.", operation: str = "registration"):
        self.first_name = first_name
        self.last_name = last_name
        self.reason = reason
        super().__init__(f"Failed to create participant {first_name} {last_name}. Reason: {reason}", operation)

class ParticipantListingError(ParticipantServiceError):
    """Raised when there's an issue listing participants."""
    def __init__(self, reason: str = "Could not retrieve list of participants.", operation: str = "list_all_participants"):
        self.reason = reason
        super().__init__(f"Failed to list participants. Reason: {reason}", operation)

class InvalidParticipantDataError(ParticipantServiceError):
    """Raised when provided data for a participant is invalid for a service operation (beyond basic validation)."""
    def __init__(self, message: str, operation: str = "processing"):
        super().__init__(message, operation)
