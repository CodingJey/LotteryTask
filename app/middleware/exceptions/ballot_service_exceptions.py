# app/middleware/exceptions/ballot_service_exceptions.py
from datetime import date
from typing import Union
from .base_exceptions import ServiceError

class BallotServiceError(ServiceError):
    """Base class for exceptions raised by the BallotService."""
    def __init__(self, message: str):
        super().__init__(message)

# --- Specific Ballot Service Exceptions ---
class BallotCreationError(BallotServiceError):
    """Raised when there's an issue creating a ballot in the repository."""
    def __init__(self, user_id: int, lottery_id: int, reason: str = "Could not create ballot in repository."):
        self.user_id = user_id
        self.lottery_id = lottery_id
        self.reason = reason
        super().__init__(f"Failed to create ballot for user ID {user_id} in lottery ID {lottery_id}. Reason: {reason}")

class BallotsNotFoundErrorForUser(BallotServiceError):
    """Raised when no ballots are found for a specific user."""
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"No ballots found for user ID {user_id}.")

class AssociatedLotteryNotFoundError(BallotServiceError):
    """
    Raised when an operation in BallotService requires a lottery that cannot be found
    (and its absence is critical for the ballot operation itself, distinct from LotteryNotFoundError
    which might be raised directly by LotteryService).
    """
    def __init__(self, identifier: Union[int, date], operation: str = "ballot submission"):
        self.identifier = identifier
        self.operation = operation
        if isinstance(identifier, date):
            super().__init__(f"Associated lottery for date {identifier.isoformat()} not found during {operation}.")
        else:
            super().__init__(f"Associated lottery with ID {identifier} not found during {operation}.")

class BallotLimitExceededError(BallotServiceError):
    """Raised if a user tries to submit more ballots than allowed for a lottery (if such a rule exists)."""
    def __init__(self, user_id: int, lottery_id: int):
        self.user_id = user_id
        self.lottery_id = lottery_id
        super().__init__(f"User ID {user_id} has exceeded the ballot limit for lottery ID {lottery_id}.")
