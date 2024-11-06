from app.services.vtex_api import VTEXAPI
from app.db.database import SessionLocal
from app.models.database_models import Product, Order, OrderItem, CartItem
from app.utils.logging import log_event
from sqlalchemy.orm import Session
import requests
import uuid

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
    
    # Obtener el ID del producto
    product_id = sku_data.get('ProductId')
    if not product_id:
        raise Exception(f"El ID del producto no está disponible para el SKU {sku_id}.")
    
    # Obtener descripción, marca e imagen
    product_description = sku_data.get('ProductDescription')
    if not product_id:
        raise Exception(f"La descripción del producto no está disponible para el SKU {sku_id}.")
    brand_name = sku_data.get('BrandName', 'Marca desconocida')
    image_url = sku_data.get('ImageUrl', '')


    # Obtener la categoría del SKU (última categoría en la jerarquía)
    category_id, category_name = get_last_category(sku_data)

    # Simulación de fulfillment para obtener precio e inventario
    items = [{"id": str(sku_id), "quantity": 1, "seller": "1"}]  # Ajusta el seller ID si es necesario
    fulfillment_data = vtex_api.simulate_fulfillment(items, sales_channel_id)

    # Extraer precio e inventario
    if not fulfillment_data.get('items'):
        raise Exception(f"No se pudo obtener información de precio e inventario para SKU {sku_id}.")
    item_info = fulfillment_data['items'][0]
    price = item_info.get('sellingPrice', 0) / 100  # Precio en la moneda local - Toma el selling price!
    inventory = item_info.get('availability')

    # Almacenar o actualizar en la base de datos
    db: Session = SessionLocal()
    existing_product = db.query(Product).filter(Product.sku_id == sku_id).first()
    if existing_product:
        # Actualizar producto existente
        existing_product.name = sku_data.get('NameComplete')
        existing_product.product_id = product_id
        existing_product.product_description = product_description
        existing_product.brand_name = brand_name
        existing_product.category_id = category_id
        existing_product.category_name = category_name
        existing_product.image_url = image_url
        existing_product.is_active = sku_data.get('IsActive')
        existing_product.price = price
        existing_product.inventory = inventory
        # Actualiza otros campos según sea necesario
    else:
        # Crear nuevo producto
        new_product = Product(
            sku_id=sku_id,
            product_id=product_id,
            name=sku_data.get('NameComplete'),
            product_description=product_description,
            brand_name=brand_name,
            category_id=category_id,
            category_name=category_name,
            image_url=image_url,
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

def get_last_category(sku_data):
    """
    Extrae la última categoría del campo ProductCategoryIds y encuentra su nombre en ProductCategories.
    """
    product_category_ids = sku_data.get('ProductCategoryIds', "")
    product_categories = sku_data.get('ProductCategories', {})

    # Si no hay categorías, lanzar excepción
    if not product_category_ids or not product_categories:
        raise Exception("No se encontraron categorías en los datos del producto.")

    # Extraer la última categoría de la lista de IDs
    category_ids = product_category_ids.strip("/").split("/")  # Remover "/" y separar los IDs
    last_category_id = category_ids[-1]  # Tomar la última categoría

    # Obtener el nombre de la categoría desde ProductCategories
    category_name = product_categories.get(last_category_id, "Categoría desconocida")

    return last_category_id, category_name

def process_notification(payload):
    sku_id = payload.get('idSKU')
    sales_channel_id = vtex_api.sales_channel_id  # Usamos el canal de ventas configurado

    # Validaciones iniciales
    if not sku_id:
        raise Exception("SKU ID no proporcionado en la notificación")

    # Procesar según los campos de la notificación
    if payload.get('HasStockKeepingUnitModified', False):
        # Si el SKU ha sido modificado o es nuevo, obtener detalles y actualizar/crear
        process_sku(sku_id, sales_channel_id)

    if payload.get('StockModified', False) or payload.get('PriceModified', False):
        # Si el inventario o precio ha cambiado, realizar simulación de fulfillment y actualizar
        update_price_and_inventory(sku_id, sales_channel_id)

    if not payload.get('isActive', True):
        # Si el producto ha sido desactivado, actualizar estado en la base de datos
        deactivate_product(sku_id)

    if payload.get('HasStockKeepingUnitRemovedFromAffiliate', False):
        # Si el SKU ya no está asociado al canal de ventas, eliminar o desactivar el producto
        remove_product_from_affiliate(sku_id)

def update_price_and_inventory(sku_id, sales_channel_id):
    # Realizar simulación de fulfillment para obtener precio e inventario actualizados
    items = [{"id": str(sku_id), "quantity": 1, "seller": "1"}]  # Ajusta el seller ID si es necesario
    fulfillment_data = vtex_api.simulate_fulfillment(items, sales_channel_id)

    # Extraer precio e inventario
    if not fulfillment_data.get('items'):
        raise Exception(f"No se pudo obtener información de precio e inventario para SKU {sku_id}.")
    item_info = fulfillment_data['items'][0]
    price = item_info.get('sellingPrice', 0) / 100  # Precio en la moneda local
    inventory = item_info.get('availability')

    # Actualizar en la base de datos
    db: Session = SessionLocal()
    existing_product = db.query(Product).filter(Product.sku_id == sku_id).first()
    if existing_product:
        existing_product.price = price
        existing_product.inventory = inventory
        db.commit()
    else:
        # Si el producto no existe, podríamos decidir crearlo o registrar un error
        db.close()
        raise Exception(f"El SKU {sku_id} no existe en la base de datos.")
    db.close()

def deactivate_product(sku_id):
    # Desactivar el producto en la base de datos
    db: Session = SessionLocal()
    existing_product = db.query(Product).filter(Product.sku_id == sku_id).first()
    if existing_product:
        existing_product.is_active = False
        existing_product.inventory = 0  # Opcional: poner inventario en cero
        db.commit()
    else:
        db.close()
        raise Exception(f"El SKU {sku_id} no existe en la base de datos.")
    db.close()

def remove_product_from_affiliate(sku_id):
    # Opcional: eliminar o desactivar el producto
    db: Session = SessionLocal()
    existing_product = db.query(Product).filter(Product.sku_id == sku_id).first()
    if existing_product:
        db.delete(existing_product)
        db.commit()
    else:
        db.close()
        raise Exception(f"El SKU {sku_id} no existe en la base de datos.")
    db.close()

# app/services/product_service.py

def update_sla_info(sku_ids, postal_code, country, client_profile_data, user_id):
    db: Session = SessionLocal()
    sku_responses = []
    try:
        # Prepare items for simulation
        items = [{"id": str(sku_id), "quantity": 1, "seller": "1"} for sku_id in sku_ids]

        # Simulate fulfillment with delivery data
        fulfillment_data = vtex_api.simulate_fulfillment_with_delivery(
            items=items,
            postal_code=postal_code,
            country=country,
            client_profile_data=client_profile_data
        )

        # Verify 'logisticsInfo' is present
        if not fulfillment_data.get('logisticsInfo'):
            raise Exception("No se pudo obtener información de logística.")

        logistics_info_list = fulfillment_data['logisticsInfo']

        # Iterate over each SKU and store SLA info in CartItem table
        for index, logistics_info in enumerate(logistics_info_list):
            sku_id = sku_ids[index]
            slas = logistics_info.get('slas', [])

            # Check inventory availability
            availability = fulfillment_data['items'][index].get('availability')
            sku_message = f"SLA actualizado para SKU {sku_id}"

            if availability != 'available':
                sku_message += " - Este SKU no tiene inventario disponible."

            if not slas:
                # Log error and add message to response
                log_event(
                    operation_id=sku_id,
                    operation="SLAUpdate",
                    direction="VTEX to Marketplace",
                    content_source=str(fulfillment_data),
                    content_translated="",
                    content_destination="",
                    business_message=f"No hay SLAs disponibles para SKU {sku_id} en la dirección proporcionada.",
                    status="Error"
                )
                sku_responses.append({
                    "sku_id": sku_id,
                    "message": f"No hay SLAs disponibles para SKU {sku_id} en la dirección proporcionada."
                })
                continue

            # Take the first available SLA (adjust as needed)
            sla = slas[0]

            # Extract required information
            sla_id = sla.get('id')
            sla_delivery_channel = sla.get('deliveryChannel')
            sla_list_price = sla.get('listPrice', 0) / 100  # Convert from cents
            sla_seller = fulfillment_data["items"][index].get("seller")
            price = fulfillment_data['items'][index].get('sellingPrice', 0) / 100
            inventory = availability

            # Create or update CartItem in the database
            cart_item = db.query(CartItem).filter(CartItem.sku_id == sku_id, CartItem.user_id == user_id).first()
            if cart_item:
                # Update existing CartItem
                cart_item.quantity += 1  # Or set quantity based on user input
                cart_item.sla_id = sla_id
                cart_item.sla_delivery_channel = sla_delivery_channel
                cart_item.sla_list_price = sla_list_price
                cart_item.sla_seller = sla_seller
                cart_item.price = price
                cart_item.inventory = inventory
            else:
                # Create new CartItem
                cart_item = CartItem(
                    sku_id=sku_id,
                    quantity=1,  # Or set quantity based on user input
                    user_id=user_id,
                    sla_id=sla_id,
                    sla_delivery_channel=sla_delivery_channel,
                    sla_list_price=sla_list_price,
                    sla_seller=sla_seller,
                    price=price,
                    inventory=inventory
                )
                db.add(cart_item)
            db.commit()

            # Log success
            log_event(
                operation_id=sku_id,
                operation="SLAUpdate",
                direction="VTEX to Marketplace",
                content_source=str(fulfillment_data),
                content_translated="Información de SLA actualizada correctamente",
                content_destination="",
                business_message=f"El SKU {sku_id} tiene nuevos datos de SLA.",
                status="Success"
            )

            # Add message to response
            sku_responses.append({
                "sku_id": sku_id,
                "message": sku_message
            })

    except Exception as e:
        raise Exception(f"Error al actualizar información de SLA: {str(e)}")
    finally:
        db.close()

    # Return list of messages for each SKU
    return sku_responses


def create_order(items, client_profile_data, postal_code, country, address_data, user_id):
    db: Session = SessionLocal()

    # Initialize variables
    order_items = []
    logistics_info = []
    total_price = 0
    sla_seller = None  # Assuming all items have the same seller

    # Iterate over each item to build order_items and logistics_info
    for index, item in enumerate(items):
        sku_id = item.sku_id
        quantity = item.quantity

        # Get SLA and price information from CartItem
        cart_item = db.query(CartItem).filter(CartItem.sku_id == sku_id, CartItem.user_id == user_id).first()
        if not cart_item:
            db.close()
            raise Exception(f"El SKU {sku_id} no existe en el carrito.")

        # Build the order item
        order_items.append({
            "id": str(sku_id),
            "quantity": quantity,
            "seller": cart_item.sla_seller,
            "price": int(cart_item.price * 100)  # Price in cents
        })

        # Build logistics info
        logistics_info.append({
            "itemIndex": index,
            "selectedSla": cart_item.sla_id,
            "selectedDeliveryChannel": cart_item.sla_delivery_channel,
            "price": int(cart_item.sla_list_price * 100)  # Price in cents
        })

        # Add to total price
        total_price += (cart_item.price + cart_item.sla_list_price) * quantity

        # Set sla_seller if not set
        if sla_seller is None:
            sla_seller = cart_item.sla_seller
        elif sla_seller != cart_item.sla_seller:
            # Handle multiple sellers if necessary
            pass

    # Generate a unique marketplaceOrderGroup
    marketplace_order_group = f"Transparent{uuid.uuid4().hex[:8]}"

    # Build the order payload
    order_payload = {
        "items": order_items,
        "clientProfileData": client_profile_data,
        "shippingData": {
            "attachmentId": "shippingData",
            "address": address_data,
            "logisticsInfo": logistics_info
        },
        "marketplaceOrderGroup": marketplace_order_group,
        "marketplaceServicesEndpoint": "https://yourmarketplace.com/mktp",  # Adjust as needed
        "marketplacePaymentValue": int(total_price * 100)  # Total price in cents
    }

    # Make the request to create the order
    endpoint = f"{vtex_api.base_url}/api/checkout/pvt/orders"
    params = {
        "sc": vtex_api.sales_channel_id,
        "affiliateId": "EXT_MKTP"  # Replace with your affiliate ID if necessary
    }
    response = requests.put(endpoint, headers=vtex_api.headers, json=order_payload, params=params)

    if response.status_code in [200, 201]:
        # Store the order in the database
        new_order = Order(
            order_id=marketplace_order_group,
            total_price=total_price,
            status="Created"
        )
        db.add(new_order)
        db.commit()

        # Store the order items
        for item in items:
            order_item = OrderItem(
                order_id=new_order.id,
                sku_id=item.sku_id,
                quantity=item.quantity,
                price=cart_item.price  # Use price from cart_item
            )
            db.add(order_item)
        db.commit()

        # Clear the CartItem entries for the SKUs in this order
        for item in items:
            db.query(CartItem).filter(CartItem.sku_id == item.sku_id, CartItem.user_id == user_id).delete()
        db.commit()
        db.close()

        # Log success
        log_event(
            operation_id=marketplace_order_group,
            operation="OrderCreation",
            direction="Marketplace to VTEX",
            content_source=str(order_payload),
            content_translated="Orden creada exitosamente",
            content_destination=response.text,
            business_message=f"La orden {marketplace_order_group} fue creada exitosamente.",
            status="Success"
        )
        return response.json()
    else:
        db.close()
        # Log error
        log_event(
            operation_id=marketplace_order_group,
            operation="OrderCreation",
            direction="Marketplace to VTEX",
            content_source=str(order_payload),
            content_translated="Error al crear la orden",
            content_destination=response.text,
            business_message=f"Error al crear la orden {marketplace_order_group}: {response.text}",
            status="Error"
        )
        raise Exception(f"Error al crear la orden: {response.status_code} - {response.text}")