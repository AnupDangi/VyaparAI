from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_bookings():
    return [{"id": 1, "customer": "Ramesh", "total": 850, "status": "pending"}]
