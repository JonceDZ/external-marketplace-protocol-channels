from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.product_service import update_sla_info, create_order

router = APIRouter()

class SLARequest(BaseModel):
    sku_id: int
    postal_code: str
    country: str
    client_profile_data: dict

@router.post("/update_sla")
def update_sla_endpoint(request: SLARequest):
    try:
        update_sla_info(
            sku_id=request.sku_id,
            postal_code=request.postal_code,
            country=request.country,
            client_profile_data=request.client_profile_data
        )
        return {"message": f"SLA actualizado para SKU {request.sku_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class OrderRequest(BaseModel):
    sku_id: int
    quantity: int
    postal_code: str
    country: str
    client_profile_data: dict
    address_data: dict

@router.post("/create_order")
def create_order_endpoint(request: OrderRequest):
    try:
        order_response = create_order(
            sku_id=request.sku_id,
            quantity=request.quantity,
            client_profile_data=request.client_profile_data,
            postal_code=request.postal_code,
            country=request.country,
            address_data=request.address_data
        )
        return {"message": "Orden creada exitosamente", "order": order_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
