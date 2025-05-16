import logging
from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from pydantic import ValidationError
from app.middleware.exceptions.lottery_service_exceptions import (
    LotteryServiceError, 
    LotteryNotFoundError,
    LotteryAlreadyExistsError,
    LotteryClosedError,
    NoBallotsFoundError,
    LotteryCreationError,
    LotteryUpdateError,
    WinnerPersistenceError,
    InvalidLotteryOperationError
)

from app.middleware.exceptions.ballot_service_exceptions import (
    BallotServiceError,
    BallotCreationError,
    BallotsNotFoundErrorForUser
)

from app.middleware.exceptions.winner_service_exceptions import (
    WinnerServiceError,
    WinnerNotFoundError,
    WinnerCreationError,
    WinnerListingError,
    DuplicateWinnerError
)

# Participant Service Exceptions
from app.middleware.exceptions.participant_service_exceptions import (
    ParticipantServiceError,
    ParticipantNotFoundError,
    ParticipantAlreadyExistsError,
    ParticipantCreationError,
    ParticipantListingError,
    InvalidParticipantDataError
)

# Configure logging
logger = logging.getLogger("app")

def register_exception_handlers(app: FastAPI):
    """
    Centralize and register exception handlers for the FastAPI application.
    Handlers are registered from most specific to most general.
    """

    # --- Custom Participant Service Exception Handlers ---
    @app.exception_handler(ParticipantNotFoundError)
    async def participant_not_found_handler(request: Request, exc: ParticipantNotFoundError) -> JSONResponse:
        logger.warning(
            f"ParticipantNotFoundError: {str(exc)} (Operation: {exc.operation})",
            extra={
                "path": request.url.path, "method": request.method,
                "identifier": exc.identifier, "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc), "type": "PARTICIPANT_NOT_FOUND"}
        )

    @app.exception_handler(ParticipantAlreadyExistsError)
    async def participant_already_exists_handler(request: Request, exc: ParticipantAlreadyExistsError) -> JSONResponse:
        logger.warning(
            f"ParticipantAlreadyExistsError: {str(exc)} (Operation: {exc.operation})",
            extra={
                "path": request.url.path, "method": request.method,
                "identifier_field": exc.identifier_field,
                "identifier_value": exc.identifier_value,
                "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, # Conflict due to existing resource
            content={"message": str(exc), "type": "PARTICIPANT_ALREADY_EXISTS"}
        )

    @app.exception_handler(ParticipantCreationError)
    async def participant_creation_error_handler(request: Request, exc: ParticipantCreationError) -> JSONResponse:
        logger.error(
            f"ParticipantCreationError: {str(exc)} (Operation: {exc.operation})",
            exc_info=True,
            extra={
                "path": request.url.path, "method": request.method,
                "first_name": exc.first_name, "last_name": exc.last_name,
                "reason": exc.reason, "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # Or 400 if data was bad post-validation
            content={"message": "Failed to register participant due to an internal issue.", "type": "PARTICIPANT_CREATION_FAILED"}
        )

    @app.exception_handler(ParticipantListingError)
    async def participant_listing_error_handler(request: Request, exc: ParticipantListingError) -> JSONResponse:
        logger.error(
            f"ParticipantListingError: {str(exc)} (Operation: {exc.operation})",
            exc_info=True,
            extra={
                "path": request.url.path, "method": request.method,
                "reason": exc.reason, "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to retrieve list of participants due to an internal issue.", "type": "PARTICIPANT_LISTING_FAILED"}
        )

    @app.exception_handler(InvalidParticipantDataError)
    async def invalid_participant_data_handler(request: Request, exc: InvalidParticipantDataError) -> JSONResponse:
        logger.warning(
            f"InvalidParticipantDataError: {str(exc)} (Operation: {exc.operation})",
            extra={
                "path": request.url.path, "method": request.method,
                "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc), "type": "INVALID_PARTICIPANT_DATA"}
        )

    # Handler for the base ParticipantServiceError
    @app.exception_handler(ParticipantServiceError)
    async def base_participant_service_error_handler(request: Request, exc: ParticipantServiceError) -> JSONResponse:
        logger.error(
            f"Unhandled ParticipantServiceError: {str(exc)} (Operation: {exc.operation})",
            exc_info=True,
            extra={
                "path": request.url.path, "method": request.method,
                "exception_type": type(exc).__name__, "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected error occurred with the participant service.", "type": "PARTICIPANT_SERVICE_ERROR"}
        )

    # --- Custom Ballot Service Exception Handlers ---
    @app.exception_handler(BallotsNotFoundErrorForUser)
    async def ballots_not_found_for_user_handler(request: Request, exc: BallotsNotFoundErrorForUser) -> JSONResponse:
        logger.warning(
            f"BallotsNotFoundErrorForUser: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "user_id": exc.user_id
            }
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc), "type": "BALLOTS_NOT_FOUND_FOR_USER"}
        )

    @app.exception_handler(BallotCreationError)
    async def ballot_creation_error_handler(request: Request, exc: BallotCreationError) -> JSONResponse:
        logger.error(
            f"BallotCreationError: {str(exc)}",
            exc_info=True, # Include stack trace for creation failures
            extra={
                "path": request.url.path,
                "method": request.method,
                "user_id": exc.user_id,
                "lottery_id": exc.lottery_id,
                "reason": exc.reason
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={"message": "Failed to create ballot due to an internal issue.", "type": "BALLOT_CREATION_FAILED"}
        )

    # Handler for the base BallotServiceError (catches any BallotServiceError not caught above)
    @app.exception_handler(BallotServiceError)
    async def base_ballot_service_error_handler(request: Request, exc: BallotServiceError) -> JSONResponse:
        logger.error(
            f"Unhandled BallotServiceError: {str(exc)}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected error occurred with the ballot service.", "type": "BALLOT_SERVICE_ERROR"}
        )

    # --- Custom Lottery Service Exception Handlers ---
    # These should come before the generic LotteryServiceError handler

    @app.exception_handler(LotteryNotFoundError)
    async def lottery_not_found_handler(request: Request, exc: LotteryNotFoundError) -> JSONResponse:
        logger.warning(
            f"LotteryNotFoundError: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "identifier": exc.identifier
            }
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc), "type": "LOTTERY_NOT_FOUND"}
        )

    @app.exception_handler(LotteryAlreadyExistsError)
    async def lottery_already_exists_handler(request: Request, exc: LotteryAlreadyExistsError) -> JSONResponse:
        logger.warning(
            f"LotteryAlreadyExistsError: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "date": exc.lottery_date.isoformat()
            }
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(exc), "type": "LOTTERY_ALREADY_EXISTS"}
        )

    @app.exception_handler(LotteryClosedError)
    async def lottery_closed_handler(request: Request, exc: LotteryClosedError) -> JSONResponse:
        logger.warning(
            f"LotteryClosedError: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "lottery_id": exc.lottery_id,
                "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, # Or 409 if preferred for state conflict
            content={"message": str(exc), "type": "LOTTERY_CLOSED"}
        )

    @app.exception_handler(NoBallotsFoundError)
    async def no_ballots_found_handler(request: Request, exc: NoBallotsFoundError) -> JSONResponse:
        logger.warning(
            f"NoBallotsFoundError: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "lottery_id": exc.lottery_id,
                "lottery_date": exc.lottery_date.isoformat()
            }
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc), "type": "NO_BALLOTS_FOUND"}
        )

    @app.exception_handler(LotteryCreationError)
    async def lottery_creation_handler(request: Request, exc: LotteryCreationError) -> JSONResponse:
        logger.error( # Log as error as it indicates a failure in a core operation
            f"LotteryCreationError: {str(exc)}",
            exc_info=True, # Include stack trace for creation failures
            extra={
                "path": request.url.path,
                "method": request.method,
                "target_date": exc.target_date.isoformat(),
                "reason": exc.reason
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to create lottery due to an internal issue.", "type": "LOTTERY_CREATION_FAILED"}
        )

    @app.exception_handler(LotteryUpdateError)
    async def lottery_update_handler(request: Request, exc: LotteryUpdateError) -> JSONResponse:
        logger.error(
            f"LotteryUpdateError: {str(exc)}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "lottery_id": exc.lottery_id,
                "operation": exc.operation,
                "reason": exc.reason
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to update lottery due to an internal issue.", "type": "LOTTERY_UPDATE_FAILED"}
        )

    @app.exception_handler(WinnerPersistenceError)
    async def winner_persistence_handler(request: Request, exc: WinnerPersistenceError) -> JSONResponse:
        logger.error(
            f"WinnerPersistenceError: {str(exc)}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "lottery_id": exc.lottery_id,
                "ballot_id": exc.ballot_id,
                "reason": exc.reason
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to save lottery winner due to an internal issue.", "type": "WINNER_PERSISTENCE_FAILED"}
        )
    
    @app.exception_handler(InvalidLotteryOperationError)
    async def invalid_lottery_operation_handler(request: Request, exc: InvalidLotteryOperationError) -> JSONResponse:
        logger.warning(
            f"InvalidLotteryOperationError: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
            }
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc), "type": "INVALID_LOTTERY_OPERATION"}
        )

    # Handler for the base LotteryServiceError (catches any LotteryServiceError not caught above)
    @app.exception_handler(LotteryServiceError)
    async def base_lottery_service_error_handler(request: Request, exc: LotteryServiceError) -> JSONResponse:
        logger.error(
            f"Unhandled LotteryServiceError: {str(exc)}",
            exc_info=True, # Good to log stack for unexpected service errors
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__
            }
        )
        # Default to 500 for unspecified service errors, or 400 if they are typically client-induced
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected error occurred with the lottery service.", "type": "LOTTERY_SERVICE_ERROR"}
        )
    
    # --- Custom Winner Service Exception Handlers ---
    @app.exception_handler(WinnerNotFoundError)
    async def winner_not_found_handler(request: Request, exc: WinnerNotFoundError) -> JSONResponse:
        logger.warning(
            f"WinnerNotFoundError: {str(exc)} (Operation: {exc.operation})",
            extra={
                "path": request.url.path,
                "method": request.method,
                "identifier": exc.identifier,
                "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc), "type": "WINNER_NOT_FOUND"}
        )

    @app.exception_handler(WinnerCreationError)
    async def winner_creation_error_handler(request: Request, exc: WinnerCreationError) -> JSONResponse:
        logger.error(
            f"WinnerCreationError: {str(exc)} (Operation: {exc.operation})",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "lottery_id": exc.lottery_id,
                "ballot_id": exc.ballot_id,
                "reason": exc.reason,
                "operation": exc.operation
            }
        )
        # This error implies an issue during a core data creation step.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to record winner due to an internal issue.", "type": "WINNER_CREATION_FAILED"}
        )

    @app.exception_handler(WinnerListingError)
    async def winner_listing_error_handler(request: Request, exc: WinnerListingError) -> JSONResponse:
        logger.error(
            f"WinnerListingError: {str(exc)} (Operation: {exc.operation})",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "reason": exc.reason,
                "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to retrieve list of winners due to an internal issue.", "type": "WINNER_LISTING_FAILED"}
        )

    @app.exception_handler(DuplicateWinnerError)
    async def duplicate_winner_error_handler(request: Request, exc: DuplicateWinnerError) -> JSONResponse:
        logger.warning(
            f"DuplicateWinnerError: {str(exc)} (Operation: {exc.operation})",
            extra={
                "path": request.url.path,
                "method": request.method,
                "lottery_id": exc.lottery_id,
                "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, # Conflict due to existing resource
            content={"message": str(exc), "type": "DUPLICATE_WINNER_FOR_LOTTERY"}
        )

    # Handler for the base WinnerServiceError (catches any WinnerServiceError not caught above)
    @app.exception_handler(WinnerServiceError)
    async def base_winner_service_error_handler(request: Request, exc: WinnerServiceError) -> JSONResponse:
        logger.error(
            f"Unhandled WinnerServiceError: {str(exc)} (Operation: {exc.operation})",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__,
                "operation": exc.operation
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected error occurred with the winner service.", "type": "WINNER_SERVICE_ERROR"}
        )

    # --- FastAPI and Pydantic Built-in Exception Handlers ---
    @app.exception_handler(FastAPIHTTPException) # Renamed to avoid conflict
    async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException) -> JSONResponse:
        logger.error(
            f"FastAPI HTTP Exception: {exc.detail}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "detail": exc.detail,
                "headers": exc.headers,
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail, "type": "HTTP_EXCEPTION"},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(
            "Request validation error.",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors()
            }
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Validation Error: The request data is invalid.",
                "details": exc.errors(),
                "type": "VALIDATION_ERROR"
            }
        )

    @app.exception_handler(ValidationError) 
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning(
            "Pydantic validation error occurred outside request cycle.",
            extra={
                "path": request.url.path,
                "method": request.method,
                "model": str(exc.model),
                "errors": exc.errors()
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # Usually an internal issue if not request validation
            content={
                "message": "Data validation processing error.",
                "details": exc.errors(),
                "type": "PYDANTIC_VALIDATION_ERROR"
            }
        )

    # --- Universal Fallback Handler (Keep this last) ---
    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.critical(
            "Critical unhandled exception occurred.",
            exc_info=True, # Includes stack trace
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected internal server error occurred. Please try again later.", "type": "UNHANDLED_EXCEPTION"}
        )

    return app