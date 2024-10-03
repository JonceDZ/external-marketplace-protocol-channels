from fastapi import APIRouter, Request, HTTPException
from app.utils.logging import log_event
from app.services.product_service import process_notification  # Importar la función que procesará la notificación

router = APIRouter()

@router.post("/")
async def receive_notification(request: Request):
    try:
        payload = await request.json()

        # Validar que el payload contiene los campos necesarios
        required_fields = [
            'idSKU', 'productId', 'an', 'idAffiliate', 'DateModified',
            'isActive', 'StockModified', 'PriceModified',
            'HasStockKeepingUnitModified', 'HasStockKeepingUnitRemovedFromAffiliate'
        ]
        for field in required_fields:
            if field not in payload:
                raise Exception(f"Campo {field} faltante en la notificación")

        # Procesar la notificación utilizando el servicio correspondiente
        process_notification(payload)

        # Registrar evento de éxito
        operation_id = payload.get('idSKU')
        log_event(
            operation_id=operation_id,
            operation="ProductUpdate",
            direction="VTEX to Marketplace",
            content_source=str(payload),
            content_translated="Notificación procesada correctamente",
            content_destination="",
            business_message=f"El SKU {operation_id} fue actualizado exitosamente en el marketplace.",
            status="Success"
        )

        return {"message": "Notificación procesada correctamente"}

    except Exception as e:
        # Registrar evento de error
        operation_id = payload.get('idSKU') if 'idSKU' in payload else 'Desconocido'
        log_event(
            operation_id=operation_id,
            operation="ProductUpdate",
            direction="VTEX to Marketplace",
            content_source=str(payload) if 'payload' in locals() else 'No disponible',
            content_translated="",
            content_destination="",
            business_message=f"Error al procesar la notificación: {str(e)}",
            status="Error"
        )
        raise HTTPException(status_code=500, detail=f"Error al procesar la notificación: {str(e)}")
