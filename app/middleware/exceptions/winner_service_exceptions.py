from datetime import date
from typing import Union
from .base_exceptions import ServiceError

class WinnerServiceError(ServiceError):
    """Base class for exceptions raised by the WinnerService."""
    def __init__(self, message: str, operation: str = "unknown"):
        self.operation = operation
        super().__init__(f"WinnerService error during {operation}: {message}")

class WinnerNotFoundError(WinnerServiceError):
    """Raised when a winning ballot is not found for a given identifier."""
    def __init__(self, identifier: Union[int, date], operation: str = "retrieval"):
        self.identifier = identifier
        if isinstance(identifier, date):
            super().__init__(f"Winning ballot for date {identifier.isoformat()} not found.", operation)
        elif isinstance(identifier, int): 
            super().__init__(f"Winning ballot associated with ID {identifier} not found.", operation)
        else:
            super().__init__(f"Winning ballot not found for identifier: {identifier}.", operation)

class WinnerCreationError(WinnerServiceError):
    """Raised when there's an issue creating a winning ballot record in the repository."""
    def __init__(self, lottery_id: int, ballot_id: int, reason: str = "Could not create winning ballot in repository.", operation: str = "record_new_winner"):
        self.lottery_id = lottery_id
        self.ballot_id = ballot_id
        self.reason = reason
        super().__init__(f"Failed to create winning ballot for Lottery ID {lottery_id}, Ballot ID {ballot_id}. Reason: {reason}", operation)

class WinnerListingError(WinnerServiceError):
    """Raised when there's an issue listing all winning ballots."""
    def __init__(self, reason: str = "Could not retrieve list of winning ballots.", operation: str = "list_all_winning_ballots"):
        self.reason = reason
        super().__init__(f"Failed to list winning ballots. Reason: {reason}", operation)

class DuplicateWinnerError(WinnerServiceError):
    """Raised if an attempt is made to record a winner for a lottery that already has one."""
    def __init__(self, lottery_id: int, operation: str = "record_new_winner"):
        self.lottery_id = lottery_id
        super().__init__(f"A winner has already been recorded for Lottery ID {lottery_id}.", operation)
