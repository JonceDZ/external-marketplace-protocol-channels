from app.db.database import SessionLocal
from app.models.database_models import Product
from sqlalchemy.orm import Session

def apply_interest(rate: float, sku_ids=None):
    """
    Aplica el interés a los precios de los SKUs especificados o a todos si sku_ids es None.
    """
    db: Session = SessionLocal()

    if sku_ids:
        products = db.query(Product).filter(Product.sku_id.in_(sku_ids)).all()
    else:
        products = db.query(Product).all()

    for product in products:
        if product.price is not None:
            product.interest_price = product.price * (1 + rate)
    db.commit()
    db.close()

def apply_discount(rate: float, sku_ids=None):
    """
    Aplica el descuento a los precios de los SKUs especificados o a todos si sku_ids es None.
    """
    db: Session = SessionLocal()

    if sku_ids:
        products = db.query(Product).filter(Product.sku_id.in_(sku_ids)).all()
    else:
        products = db.query(Product).all()

    for product in products:
        if product.price is not None:
            product.discount_price = product.price * (1 - rate)
    db.commit()
    db.close()

def apply_tax(rate: float, sku_ids=None):
    """
    Aplica el impuesto a los precios de los SKUs especificados o a todos si sku_ids es None.
    """
    db: Session = SessionLocal()

    if sku_ids:
        products = db.query(Product).filter(Product.sku_id.in_(sku_ids)).all()
    else:
        products = db.query(Product).all()

    for product in products:
        if product.price is not None:
            product.taxed_price = product.price * (1 + rate)
    db.commit()
    db.close()

def set_marketplace_inventory(sku_id: int, inventory: int):
    """
    Establece el inventario propio del marketplace para un SKU específico.
    """
    db: Session = SessionLocal()

    # Buscar el producto por SKU
    product = db.query(Product).filter(Product.sku_id == sku_id).first()

    if product:
        product.marketplace_inventory = inventory  # Actualizar el inventario del marketplace
        db.commit()
    else:
        db.close()
        raise Exception(f"El SKU {sku_id} no existe en la base de datos.")
    
    #db.commit()
    db.close()
