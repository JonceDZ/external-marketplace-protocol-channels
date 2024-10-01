from app.services.vtex_api import VTEXAPI
from app.db.database import SessionLocal
from app.models.database_models import Product
from app.utils.logging import log_event
from sqlalchemy.orm import Session

vtex_api = VTEXAPI()

def process_initial_load(sales_channel_id):
    try:
        sku_ids = vtex_api.get_sku_ids_by_sales_channel(sales_channel_id)
        for sku_id in sku_ids:
            try:
                process_sku(sku_id, sales_channel_id)
            except Exception as e:
                # Registrar error en logs y continuar con el siguiente SKU
                log_event(
                    operation_id=sku_id,
                    operation="ProductLoad",
                    direction="VTEX to Marketplace",
                    content_source=f"SKU ID: {sku_id}",
                    content_translated="",
                    content_destination="",
                    business_message=f"Error al procesar el SKU {sku_id}: {str(e)}",
                    status="Error"
                )
                continue
    except Exception as e:
        raise Exception(f"Error en la carga inicial: {str(e)}")

def process_sku(sku_id, sales_channel_id):
    # Obtener detalles del SKU
    sku_data = vtex_api.get_sku_and_context(sku_id)

    # Validaciones
    if not sku_data.get('IsActive'):
        raise Exception(f"SKU {sku_id} está inactivo.")
    if sales_channel_id not in sku_data.get('SalesChannels', []):
        raise Exception(f"SKU {sku_id} no está asociado al canal de ventas {sales_channel_id}.")
    if not sku_data.get('IsProductActive'):
        raise Exception(f"Producto del SKU {sku_id} está inactivo.")

    # Simulación de fulfillment para obtener precio e inventario
    items = [{"id": str(sku_id), "quantity": 1, "seller": "1"}]  # Ajusta el seller ID si es necesario
    fulfillment_data = vtex_api.simulate_fulfillment(items, sales_channel_id)

    # Extraer precio e inventario
    if not fulfillment_data.get('items'):
        raise Exception(f"No se pudo obtener información de precio e inventario para SKU {sku_id}.")
    item_info = fulfillment_data['items'][0]
    price = item_info.get('price', 0) / 100  # Precio en la moneda local
    inventory = item_info.get('availability')

    # Almacenar o actualizar en la base de datos
    db: Session = SessionLocal()
    existing_product = db.query(Product).filter(Product.sku_id == sku_id).first()
    if existing_product:
        # Actualizar producto existente
        existing_product.name = sku_data.get('NameComplete')
        existing_product.is_active = sku_data.get('IsActive')
        existing_product.price = price
        existing_product.inventory = inventory
        # Actualiza otros campos según sea necesario
    else:
        # Crear nuevo producto
        new_product = Product(
            sku_id=sku_id,
            name=sku_data.get('NameComplete'),
            is_active=sku_data.get('IsActive'),
            price=price,
            inventory=inventory
            # Añade otros campos necesarios
        )
        db.add(new_product)
    db.commit()
    db.close()

    # Registrar éxito en logs
    log_event(
        operation_id=sku_id,
        operation="ProductLoad",
        direction="VTEX to Marketplace",
        content_source=str(sku_data),
        content_translated="Producto procesado y almacenado correctamente",
        content_destination="",
        business_message=f"El SKU {sku_id} fue procesado exitosamente.",
        status="Success"
    )
