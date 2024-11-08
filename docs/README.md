# External Marketplace Protocol Transparente

El objetivo de este proyecto es ofrecer una aplicación que permita a los VTEXers entender cómo opera una integración basada en el External Marketplace Protocol de VTEX. Se denomina transparente porque busca ofrecer la perspectiva de ambos lados: tanto desde el seller VTEX como del marketplace externo.

## Tecnologías utilizadas
* **Backend:** Python 3.9.6, FastAPI, Uvicorn
* **Base de Datos:** SQLite (con posibilidad de migrar a PostgreSQL)
* **ORM:** SQLAlchemy
* **Validación de Datos:** Pydantic
* **Cliente HTTP:** requests
* **Interfaz de Usuario (UI):** Jinja2 (posibilidad de utilizar Vue.js en el futuro)
* **Gestión de Dependencias:** pip y requirements.txt
* **Entorno Virtual:** conda

## Configuración Inicial
### Prerrequisitos
* Tener conda instalado en tu sistema.
* Tener acceso a una cuenta VTEX y sus credenciales (App Key y App Token).

### Instalación
1. Clonar el repositorio:
```
git clone https://github.com/JonceDZ/external-marketplace-protocol-channels.git
```
2. Navegar al directorio del proyecto:
```
cd external-marketplace-protocol-channels
```
3. Crear y activar el entorno virtual usando conda:
```
conda create --name vtex-marketplace python=3.9.6
conda activate vtex-marketplace
```
4. Instalar las dependencias:
```
pip install -r requirements.txt
```
### Configuración de Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
VTEX_APP_KEY= {X-VTEX-API-AppKey}
VTEX_APP_TOKEN= {X-VTEX-API-AppToken}
VTEX_ACCOUNT_NAME= {accountName}
VTEX_API_URL=https://{accountName}.vtexcommercestable.com.br/api
SALES_CHANNEL_ID= {tradePolicy}
```
_Reemplaza `tu_app_key`, `tu_app_token`, `tu_account_name` y `tu_sales_channel_id` con los valores correspondientes de tu cuenta VTEX._

## Ejecución del proyecto

Para que el proyecto pueda correr sin problemas, es necesario tener en cuenta las siguientes **anotaciones y limitaciones** del mismo:
* Se debe tener una configuración logística específica para este canal, la cual debe tener la capacidad de despachar a nivel nacional. A partir de esta configuración se evitan escenarios en los que se muestre algún producto como disponible en el front del marketplace externo, pero que luego no esté disponible para despachar a zonas específicas.
* Debido a la configuración y lógica que tiene el marketplace, solo funciona con cuentas que no tengan ningún tipo de impuesto (tax) configurado. Esto porque se toma el `sellingPrice` y valor logístico como criterios para el cálculo del valor final; de momento no se tienen en cuenta impuestos. _Cabe resaltar que no se descarta implementar esta funcionalidad en versiones futuras_

Teniendo en cuenta esto, se puede proceder con la ejecución:
1. Inicia el servidor FastAPI:
```
uvicorn app.main:app --reload
```
2. Accede a la aplicación en tu navegador:
* **Aplicación:** http://127.0.0.1:8000
* **Documentación interactiva (Swagger UI):** http://127.0.0.1:8000/docs

## Estructura del Proyecto
La estructura general del proyecto es la siguiente:
```
external-marketplace-protocol-channels/
├── app/
│   ├── main.py                   # Punto de entrada de la aplicación
│   ├── api/
│   │   └── routes/
│   │       ├── notifications.py   # Endpoints para notificaciones desde VTEX
│   │       ├── logs.py            # Endpoints para obtener logs
│   │       ├── products.py        # Endpoints para manejo de productos
│   │       └── orders.py          # Endpoints para manejo de órdenes
│   ├── config/
│   │   └── settings.py            # Configuración y variables de entorno
│   ├── db/
│   │   └── database.py            # Configuración de la base de datos
│   ├── models/
│   │   └── database_models.py     # Modelos de datos
│   ├── services/
│   │   ├── product_service.py     # Lógica de negocio para productos y órdenes
│   │   └── vtex_api.py            # Cliente para interacción con la API de VTEX
│   ├── templates/                 # Plantillas HTML (vacío por ahora)
│   └── utils/
│       └── logging.py             # Utilidades para logging
├── docs/
│   ├── ARCHITECTURE.md            # Documentación de arquitectura
│   └── README.md                  # Este archivo
├── .env                           # Variables de entorno (no se sube al repositorio)
├── .gitignore                     # Archivos ignorados por Git
├── requirements.txt               # Dependencias del proyecto
└── vtex_marketplace.db            # Base de datos SQLite generada
```

## Flujo de datos

1. **Carga Inicial y Actualización del Catálogo:**
* **Carga Inicial:** Obtiene todos los SKUs asociados al canal de ventas configurado en VTEX y los almacena en la base de datos local.
* **Notificaciones:** Recibe notificaciones desde VTEX cuando hay actualizaciones en productos o SKUs y actualiza la base de datos en consecuencia.

2. **Gestión de Órdenes:**
* **Agregar Ítems al Carrito:** Simula fulfillment para obtener información de SLA y almacena los datos en una tabla temporal, simulando el comportamiento de un carrito (`CartItem`).
* **Crear Órdenes:** Valida que los ítems y cantidades en el carrito coincidan con la solicitud y crea la orden en VTEX, almacenando los detalles en la base de datos.
* **Autorizar y Facturar Órdenes:** Envía notificaciones a VTEX para autorizar y facturar las órdenes, permitiendo que avancen en el flujo de procesamiento, llegando hasta status `Facturado` en VTEX.
3. **Logging:**
* Registra eventos clave y errores en una tabla de logs, siguiendo las especificaciones de VTEX.

## Endpoints y Servicios
### Catálogo
#### Carga Inicial de Productos
Endpoint:
```
POST /products/initial_load/
```
* **Descripción:**
Realiza la carga inicial de productos desde VTEX, obteniendo todos los SKUs asociados a la política comercial configurada y almacenándolos en la base de datos local.

* **Proceso:**

    1. **Obtención de SKUs:** Utiliza `vtex_api.get_sku_ids_by_sales_channel` para obtener los SKU IDs.
    2. **Procesamiento de SKUs:** Para cada SKU, se obtienen los detalles y se almacenan en la base de datos mediante process_sku.
    3. **Validaciones:** Se asegura que el SKU y el producto estén activos y asociados al canal de ventas.
    4. **Simulación de Fulfillment:** Obtiene precio e inventario mediante `simulate_fulfillment`.
    5. **Registro de Logs:** Cada operación se registra en el sistema de logs.

#### Recepción de Notificaciones
Endpoint:
```
POST /notifications/
```
* **Descripción:**
Recibe notificaciones de VTEX cuando hay actualizaciones en productos o SKUs y procesa los cambios en la base de datos.

* **Proceso:**

    1. **Validación de Payload:** Verifica que la notificación contenga todos los campos necesarios.
    2. **Procesamiento de la Notificación:** Dependiendo de los campos, puede crear, actualizar o eliminar productos mediante `process_notification`.
    3. **Registro de Logs:** Registra el éxito o error de la operación en los logs.

* **Campos Clave en la Notificación:**
    * `idSKU`, `productId`, `an`, `idAffiliate`, `DateModified`, `isActive`, `StockModified`, `PriceModified`, `HasStockKeepingUnitModified`, `HasStockKeepingUnitRemovedFromAffiliate`.

### Órdenes
#### Agregar Ítems al Carrito
Endpoint:
```
POST /orders/add_to_cart
```
* **Descripción:**
Agrega ítems al carrito, simulando fulfillment para obtener información de SLA y almacenando los datos en la base de datos.

Parámetros de Solicitud:
```
{
    "items": [
        {
            "sku_id": 1,
            "quantity": 2
        },
        {
            "sku_id": 1,
            "quantity": 1
        }
    ],
    "postal_code": "11001",
    "country": "COL",
    "client_profile_data": {
        "email": "clark.kent@example.com",
        "firstName": "Clark",
        "lastName": "Kent",
        "documentType": "cedulaCol",
        "document": "12345678900",
        "phone": "+573014444444"
    }
}
```
* **Proceso:**

    1. **Simulación de Fulfillment con Entrega:** Utiliza `simulate_fulfillment_with_delivery` para obtener SLAs.
    2. **Almacenamiento en `CartItem`:** Guarda los datos de SLA en la tabla temporal `CartItem`.
    3. **Validaciones:** Si no hay SLAs disponibles o el SKU no está en el carrito, se registra un error.

#### Crear Órdenes
Endpoint:
```
POST /orders/create_order
```
* **Descripción:**
Crea una orden en VTEX con los SKUs y cantidades especificados, asegurando que coincidan con los datos en el carrito.

Parámetros de Solicitud:
```
{
    "items": [
        {
            "sku_id": 1,
            "quantity": 2
        },
        {
            "sku_id": 2,
            "quantity": 1
        }
    ],
    "postal_code": "11001",
    "country": "COL",
    "client_profile_data": {
        "email": "clark.kent@example.com",
        "firstName": "Clark",
        "lastName": "Kent",
        "documentType": "cedulaCol",
        "document": "12345678900",
        "phone": "+573014444444"
    },
    "address_data": {
        "addressType": "residential",
        "receiverName": "Clark Kent",
        "postalCode": "11001",
        "city": "Bogotá",
        "state": "Bogotá D.C.",
        "country": "COL",
        "street": "Calle Falsa",
        "number": "123",
        "neighborhood": "Centro",
        "complement": "Apt 456",
        "reference": "Cerca del parque"
    }
}
```

* **Proceso:**

    1. **Validación de Carrito vs Solicitud:** Asegura que los SKUs y cantidades en la solicitud coincidan con los del carrito.
    2. **Construcción de la Orden:** Prepara los datos para enviar a VTEX.
    3. **Creación de la Orden en VTEX:** Utiliza el endpoint de VTEX para crear la orden.
    4. **Almacenamiento en la Base de Datos:** Guarda la orden y los detalles en la tabla Order.
    5. **Limpieza del Carrito:** Elimina los CartItem del usuario.

#### Autorizar y Facturar Órdenes
Endpoint:
```
POST /orders/authorize_and_invoice/{order_id}
```

* ***Descripción:***
Autoriza y factura una orden en VTEX, permitiendo que avance en el flujo de procesamiento.

* **Parámetros de Ruta:**
    * `order_id`: Identificador de la orden creada previamente.

* **Proceso:**
    1. **Autorización de la Orden:** Envía una notificación a VTEX autorizando la orden.
    2. **Facturación de la Orden:** Envía la información de facturación a VTEX.
    3. **Actualización del Estado:** Cambia el estado de la orden a `Invoiced` en la base de datos.
    4. **Registro de Logs:** Registra el éxito o error de la operación en los logs.

Ejemplo de Solicitud:
```
curl -X POST "http://127.0.0.1:8000/orders/authorize_and_invoice/{order_id}" \
-H "Content-Type: application/json"
```
*Reemplaza {order_id} con el ID de la orden que deseas autorizar y facturar. El ID de la orden corresponde al que se almacenó en la BBDD local (sin el ID del afiliado ni el "01"*

### Logs
Endpoint:
```
GET /{vtexaccount}/logs/
```
* **Descripción:**
Obtiene los logs registrados, filtrando por fecha y estado.

* **Parámetros de Consulta:**
    * `DateAt:` Fecha en formato `aaaa-mm-dd`.
    * `status`: Estado de los logs (`all`, `success`, `error`, `alert`, `pending`).
* **Respuesta:**
Devuelve una lista de mensajes con los detalles de los eventos registrados.

## Modelos de Datos
### Product
* **Descripción:**
Representa los productos obtenidos desde VTEX.

* **Campos Principales:**
    * `sku_id`: Identificador único del SKU en VTEX.
    *`product_id`: Identificador único del producto en VTEX.
    *`name`: Nombre del producto.
    *`product_description`: Descripción del producto.
    *`brand_name`: Nombre de la marca.
    *`category_id`: ID de la categoría.
    *`category_name`: Nombre de la categoría.
    *`image_url`: URL de la imagen.
    *`is_active`: Estado del SKU.
    *`price`: Precio del producto.
    *`inventory`: Disponibilidad del producto.

### Order
* **Descripción:**
Representa una orden creada en VTEX.

* **Campos Principales:**
    * `order_id`: Identificador único de la orden en VTEX.
    * `total_price`: Precio total de la orden.
    * `order_date`: Fecha de creación.
    * `status`: Estado de la orden.
    * `items`: Lista de ítems en formato JSON, cada uno con sku_id, quantity y price.

### CartItem
* **Descripción:**
Tabla temporal que almacena los ítems agregados al carrito por un usuario.

* **Campos Principales:**
    *`sku_id`: Identificador del SKU.
    *`quantity`: Cantidad agregada.
    *`sla_id`: ID del SLA seleccionado.
    *`sla_delivery_channel`: Canal de entrega.
    *`sla_list_price`: Precio del SLA.
    *`sla_seller`: Vendedor.
    *`price`: Precio del SKU.
    *`inventory`: Disponibilidad.
    *`user_id`: Identificador del usuario.

### LogEntry
* **Descripción:**
Registra eventos y errores para seguimiento y auditoría.

* **Campos Principales:**
    *`OperationId`: ID único de la operación.
    *`Operation`: Tipo de operación realizada.
    *`Direction`: Origen y destino de la información.
    *`ContentSource`: Payload enviado por el origen.
    *`ContentTranslated`: Mensaje transformado por el conector.
    *`ContentDestination`: Payload enviado al destino.
    *`BusinessMessage`: Mensaje explicativo.
    *`Status`: Estado del log (Success, Error, etc.).
    *`Timestamp`: Fecha y hora del evento.

## Buenas Prácticas de Seguridad
* **Manejo de Credenciales:** Las credenciales y datos sensibles se manejan mediante variables de entorno y no se incluyen en el repositorio.
* **Validación de Datos:** Se validan las entradas en los endpoints para evitar inyecciones y datos malformados.
* **Control de Acceso:** Aunque el proyecto es educagitivo, se recomienda implementar autenticación y autorización para endpoints sensibles.
* **Registro de Errores:** Los errores se registran detalladamente en los logs para facilitar la detección y solución de problemas.

