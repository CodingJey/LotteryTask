import time
import logging
import uuid
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.responses import StreamingResponse  # Import StreamingResponse

logger = logging.getLogger("app")  # Get logger instance

async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Generate unique request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log request start
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None
        }
    )

    try:
        response = await call_next(request)
    except Exception as e:
        # Log error with request ID
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "traceback": e.__traceback__
            },
            exc_info=True
        )
        raise

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    # Calculate response size, handling StreamingResponse
    response_size = 0
    if isinstance(response, Response):
        if hasattr(response, "body") and response.body: # More robust check for body
            response_size = len(response.body)
    elif isinstance(response, StreamingResponse):
        content_length_header = response.headers.get("Content-Length")
        if content_length_header:
            try:
                response_size = int(content_length_header)
            except ValueError:
                response_size = 0

    # Log request completion
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "processing_time": formatted_process_time,
            "status_code": response.status_code,
            "response_size": response_size  # Use calculated response_size
        }
    )

    return response