from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_chats():
    return [{"id": 1, "name": "Rakesh Bhai", "lastMsg": "2 Maggi bhejo"}]
