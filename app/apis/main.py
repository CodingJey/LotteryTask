from fastapi import APIRouter
from app.apis.routes import participant_routes

main_router = APIRouter(prefix="/lottery", tags=["lottery"])

#Adding routes to Main Router
main_router.include_router(participant_routes.router)
