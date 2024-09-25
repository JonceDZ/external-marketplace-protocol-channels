from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def receive_notification():
    return {"message": "Notification endpoint working!"}