from fastapi import FastAPI
import logging
from logging.config import dictConfig
from app.apis.main import main_router
from app.middleware.exception_handler import register_exception_handlers
from app.configs.config import LOGGING_CONFIG
from app.middleware.request_logger import log_requests 

backend_server = FastAPI( title="JS Programming Labs", description="server side backend renderer", version="1.0.0")

def create_app(app : FastAPI) -> FastAPI:

    dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("app") 

    app.include_router(main_router) 
    
    #Middlewares
    app.middleware("http")(log_requests) 
    app = register_exception_handlers(app)

    logger.info("FastAPI app created")
    return app

backend_server = create_app(backend_server)