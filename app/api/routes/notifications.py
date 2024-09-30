from fastapi import APIRouter

router = APIRouter()

@router.post("/")   # aquí podemos agregar aún más trozo de path para poder diferenciar la función y lo que va a procesar.
async def receive_notification():
    return {"message": "Notification endpoint working!"}