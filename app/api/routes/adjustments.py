from fastapi import APIRouter, HTTPException
from app.services.adjustment_service import apply_interest, apply_discount, apply_tax, set_marketplace_inventory
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

router = APIRouter()

class SKUAdjustment(BaseModel):
    rate: float = Field(..., ge=0, le=1, description="La tasa debe estar entre 0 y 1")  # Tasa a aplicar
    sku_ids: Optional[List[int]] = None  # Lista de SKUs a ajustar; si es None, aplica a todos

class InventoryAdjustment(BaseModel):
    sku_id: int  # SKU específico
    inventory: int  # Cantidad de inventario

@router.post("/apply_interest")
def apply_interest_endpoint(adjustment: SKUAdjustment):
    try:
        apply_interest(rate=adjustment.rate, sku_ids=adjustment.sku_ids)
        return {"message": "Interés aplicado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply_discount")
def apply_discount_endpoint(adjustment: SKUAdjustment):
        try:
            apply_discount(rate=adjustment.rate, sku_ids=adjustment.sku_ids)
            return {"message": "Descuento aplicado exitosamente"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply_tax")
def apply_tax_endpoint(adjustment: SKUAdjustment):
    try:
        apply_tax(rate=adjustment.rate, sku_ids=adjustment.sku_ids)
        return {"message": "Impuesto aplicado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set_marketplace_inventory")
def set_marketplace_inventory_endpoint(adjustment: InventoryAdjustment):
    try:
        set_marketplace_inventory(sku_id=adjustment.sku_id, inventory=adjustment.inventory)
        return {"message": f"Inventario del SKU {adjustment.sku_id} establecido en {adjustment.inventory} unidades exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
