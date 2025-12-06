from fastapi import APIRouter
from config.db import get_db_connection

router = APIRouter()

@router.get("/")
def get_bookings():
    # Placeholder for booking logic
    return []
