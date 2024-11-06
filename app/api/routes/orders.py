from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.product_service import update_sla_info, create_order

router = APIRouter()

class SLARequest(BaseModel):
    sku_ids: list[int]
    postal_code: str
    country: str
    client_profile_data: dict

class OrderItem(BaseModel):  # Define primero OrderItem
    sku_id: int
    quantity: int

class OrderRequest(BaseModel):
    items: list[OrderItem]
    postal_code: str
    country: str
    client_profile_data: dict
    address_data: dict


def get_current_user_id():
    # Implement logic to retrieve current user ID
    return 1  # Placeholder

@router.post("/update_sla")
def update_sla_endpoint(request: SLARequest, user_id: int = Depends(get_current_user_id)):
    try:
        sku_responses = update_sla_info(
            sku_ids=request.sku_ids,
            postal_code=request.postal_code,
            country=request.country,
            client_profile_data=request.client_profile_data,
            user_id=user_id
        )
        return {"messages": sku_responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_order")
def create_order_endpoint(request: OrderRequest, user_id: int = Depends(get_current_user_id)):
    try:
        order_response = create_order(
            items=request.items,
            client_profile_data=request.client_profile_data,
            postal_code=request.postal_code,
            country=request.country,
            address_data=request.address_data,
            user_id=user_id
        )
        return {"message": "Orden creada exitosamente", "order": order_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_order")
def create_order_endpoint(request: OrderRequest):
    try:
        order_response = create_order(
            items=request.items,
            client_profile_data=request.client_profile_data,
            postal_code=request.postal_code,
            country=request.country,
            address_data=request.address_data
        )
        return {"message": "Orden creada exitosamente", "order": order_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
