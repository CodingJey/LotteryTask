from fastapi import APIRouter
from app.apis.routes import main_routes

api_router = APIRouter()

#Adding Subscription API
api_router.include_router(main_routes.router)
