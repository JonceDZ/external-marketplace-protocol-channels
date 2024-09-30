from fastapi import APIRouter, Request, HTTPException
from app.utils.logging import log_event

router = APIRouter()

@router.post("/")   # aquí podemos agregar aún más trozo de path para poder diferenciar la función y lo que va a procesar.
async def receive_notification():
    return {"message": "Notification endpoint working!"}

@router.post("/")
async def receive_notification(request: Request):
    try:
        payload = await request.json()
        # Procesamiento de la notificación...

        # Ejemplo de registro de un evento de éxito (S1)
        operation_id = 13  # Debe ser un identificador único
        log_event(
            operation_id=operation_id,
            operation="ProductUpdate",
            direction="VTEX to Marketplace",
            content_source=str(payload),
            content_translated="Producto actualizado correctamente",
            content_destination="",
            business_message="El SKU (ID y nombre) fue actualizado exitosamente en el marketplace.",
            status="Success"
        )

        return {"message": "Notificación procesada correctamente"}

    except Exception as e:
        # Ejemplo de registro de un evento de error (E1)
        operation_id = 14  # Debe ser un identificador único
        log_event(
            operation_id=operation_id,
            operation="ProductUpdate",
            direction="VTEX to Marketplace",
            content_source=str(payload),
            content_translated="",
            content_destination="",
            business_message=f"Error al procesar la notificación: {str(e)}",
            status="Error"
        )
        raise HTTPException(status_code=500, detail="Error al procesar la notificación")
