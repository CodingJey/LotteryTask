from datetime import date
from typing import Union
from.base_exceptions import ServiceError


class LotteryServiceError(ServiceError):
    """Base class for exceptions raised by the LotteryService."""
    def __init__(self, message: str):
        super().__init__(message)

# --- Specific Lottery Service Exceptions ---
class LotteryNotFoundError(LotteryServiceError):
    """Raised when a lottery is not found."""
    def __init__(self, identifier: Union[int, date]):
        self.identifier = identifier
        if isinstance(identifier, date):
            super().__init__(f"Lottery for date {identifier.isoformat()} not found.")
        else:
            super().__init__(f"Lottery with ID {identifier} not found.")

class LotteryAlreadyExistsError(LotteryServiceError):
    """Raised when attempting to create a lottery that already exists for a given date."""
    def __init__(self, lottery_date: date):
        self.lottery_date = lottery_date
        super().__init__(f"A lottery already exists for the date {lottery_date.isoformat()}.")

class LotteryClosedError(LotteryServiceError):
    """Raised when an operation is attempted on a lottery that is already closed."""
    def __init__(self, lottery_id: int, operation: str = "The operation"):
        self.lottery_id = lottery_id
        self.operation = operation
        super().__init__(f"{operation} cannot be performed: Lottery ID {lottery_id} is already closed.")

class NoBallotsFoundError(LotteryServiceError):
    """Raised when no ballots are found for a lottery during a draw."""
    def __init__(self, lottery_id: int, lottery_date: date):
        self.lottery_id = lottery_id
        self.lottery_date = lottery_date
        super().__init__(f"No ballots found for lottery ID {lottery_id} (date: {lottery_date.isoformat()}) to perform a draw.")

class LotteryCreationError(LotteryServiceError):
    """Raised when there's an issue creating a lottery in the repository."""
    def __init__(self, target_date: date, reason: str = "Could not create lottery in repository."):
        self.target_date = target_date
        self.reason = reason
        super().__init__(f"Failed to create lottery for date {target_date.isoformat()}. Reason: {reason}")

class LotteryUpdateError(LotteryServiceError):
    """Raised when there's an issue updating a lottery (e.g., marking as closed)."""
    def __init__(self, lottery_id: int, operation: str = "update", reason: str = "Repository update failed."):
        self.lottery_id = lottery_id
        self.operation = operation
        self.reason = reason
        super().__init__(f"Failed to {operation} lottery ID {lottery_id}. Reason: {reason}")

class WinnerPersistenceError(LotteryServiceError):
    """Raised when there's an issue persisting the winning ballot."""
    def __init__(self, lottery_id: int, ballot_id: int, reason: str = "Could not save winning ballot."):
        self.lottery_id = lottery_id
        self.ballot_id = ballot_id
        self.reason = reason
        super().__init__(f"Failed to persist winner (Ballot ID: {ballot_id}) for Lottery ID: {lottery_id}. Reason: {reason}")

class InvalidLotteryOperationError(LotteryServiceError):
    """Raised for logically invalid operations not covered by other specific exceptions."""
    def __init__(self, message: str):
        super().__init__(message)