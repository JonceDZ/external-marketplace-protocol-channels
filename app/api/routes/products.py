from fastapi import APIRouter, HTTPException
from app.services.product_service import process_initial_load
from app.config.settings import settings

router = APIRouter()

@router.post("/initial_load/")
def initial_load():
    try:
        sales_channel_id = settings.sales_channel_id  # Obtener sales_channel_id del archivo .env
        process_initial_load(sales_channel_id)
        return {"message": "Carga inicial completada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
