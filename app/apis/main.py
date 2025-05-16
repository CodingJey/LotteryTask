from fastapi import APIRouter
from app.apis.routes import participant_routes, lottery_routes, ballot_routes, winner_ballots_routes

main_router = APIRouter(prefix="/api/v1", tags=["lottery"])

#Adding routes to Main Router
main_router.include_router(participant_routes.router)
main_router.include_router(lottery_routes.router)
main_router.include_router(ballot_routes.router)
main_router.include_router(winner_ballots_routes.router)
