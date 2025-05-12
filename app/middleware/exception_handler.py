import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from slowapi.errors import RateLimitExceeded
from pydantic import ValidationError

# Configure logging
logger = logging.getLogger("app")

def register_exception_handlers(app):
    """
    Centralize and register exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    
    Returns:
        FastAPI application with registered exception handlers
    """
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        """
        Handle rate limit exceeded errors with detailed logging.
        
        Args:
            request: Incoming request details
            exc: Rate limit exceeded exception
        
        Returns:
            JSON response with 429 status code
        """
        logger.warning(
            "Rate limit exceeded",
            extra={
                "path": request.url.path,
                "method": request.method,
                "client_host": request.client
            }
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"message": "Too many requests, please try again later"}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTP-specific exceptions with detailed logging.
        
        Args:
            request: Incoming request details
            exc: HTTP exception
        
        Returns:
            JSON response with the exception's status code
        """
        logger.error(
            f"HTTP Exception: {exc.detail}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle request validation errors with detailed logging.
        
        Args:
            request: Incoming request details
            exc: Validation error exception
        
        Returns:
            JSON response with 422 status code and validation errors
        """
        logger.warning(
            "Request validation error",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors()
            }
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Validation error",
                "details": exc.errors()
            }
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """
        Handle Pydantic model validation errors with detailed logging.
        
        Args:
            request: Incoming request details
            exc: Pydantic validation error
        
        Returns:
            JSON response with 500 internal server error status
        """
        logger.warning(
            "Pydantic validation error",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors()
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Universal exception handler for unhandled exceptions.
        Provides a consistent error response and logs detailed error information.
        
        Args:
            request: Incoming request details
            exc: Unhandled exception
        
        Returns:
            JSON response with 500 internal server error status
        """
        logger.error(
            "Unhandled exception occurred",
            exc_info=exc,
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

    return app