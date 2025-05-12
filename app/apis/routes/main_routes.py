from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import logging 

logger = logging.getLogger("app")

router = APIRouter()

@router.get("/")
async def root_page(request: Request):
    """
    Render the home page
    """
    return "Hello world"


