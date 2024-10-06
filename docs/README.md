# External Marketplace Protocol Transparente
El fin de este desarrollo es ofrecer una aplicación que permita a los VTEXers entender la manera en cómo opera una integración basada en el External Marketplace Protocol. 
Se denomina transparente, ya que busca ofrecer la perspectiva de ambos lados, tanto desde el seller VTEX, como del Marketplace externo.

## Tecnologías Utilizadas
- **Backend:** Python 3.9.6, FastAPI, Uvicorn
- **Base de Datos:** SQLite (posibilidad de migrar a PostgreSQL)
- **Interfaz de Usuario:** Jinja2, HTML/CSS
- **Cliente HTTP:** requests
- **ORM:** SQLAlchemy
- **Gestión de Dependencias:** pip
- **Entorno Virtual:** conda

## Configuración Inicial

### Prerrequisitos
- Tener `conda` instalado en tu sistema.
- Tener acceso a un repositorio de VTEX y sus credenciales.

### Instalación
1. Clona el repositorio.
2. Navega al directorio del proyecto: `cd external-marketplace-protocol-channels`
3. Crea y activa el entorno virtual usando conda: 
```
conda create --name vtex-marketplace python=3.9.6
conda activate vtex-marketplace
```
4. Instala las dependencias: `pip install -r requirements.txt`

### Configuración de Variables de Entorno
Crea un archivo .env en la raíz del proyecto con las siguientes variables:
```
VTEX_APP_KEY=your_app_key
VTEX_APP_TOKEN=your_app_token
VTEX_ACCOUNT_NAME={accountName}
VTEX_API_URL=https://{accountName}.vtexcommercestable.com.br/api
```

## Cómo Ejecutar el Proyecto
1. Inicia el servidor FastAPI: `uvicorn app.main:app --reload`

2. Accede a la aplicación en tu navegador: http://127.0.0.1:8000
Para ver la documentación interactiva generada por FastAPI, visita: http://127.0.0.1:8000/docs

## Estructura del Proyecto
La estructura del proyecto se ha detallado en ARCHITECTURE.md. Consulta ese archivo para entender cómo está organizada la aplicación y cómo se integran los diferentes componentes.

## Servicio de Logging
El servicio de logging está diseñado para cumplir con las especificaciones de VTEX, permitiendo que el marketplace externo registre y exponga los logs de interacción con VTEX.

* Modelo de Datos:`LogEntry` incluye los campos requeridos por VTEX.
* Endpoint de Logs: Expuesto en `/{vtexaccount}/logs/`, acepta los parámetros `DateAt` y `status`.
* Formato de Mensajes: Los logs siguen el estándar definido por VTEX, incluyendo códigos de evento y mensajes amigables.
* Uso en la Aplicación: Los logs se registran utilizando la función `log_event` en los puntos clave de interacción con VTEX.

## Carga Inicial de Productos desde VTEX
La aplicación cuenta con un servicio que realiza la carga inicial de productos desde VTEX, obteniendo información detallada de los SKUs asociados al canal de ventas configurado y almacenándola en la base de datos del marketplace.

### Proceso de Carga Inicial
* **Obtención de SKUs:** La aplicación interactúa con el endpoint de VTEX para obtener la lista de SKU IDs asociados al canal de ventas especificado.
* **Validación de Productos y SKUs:** Para cada SKU obtenido, se realizan las siguientes validaciones:
    * El SKU está activo (`isActive`).
    * El SKU está asociado al canal de ventas configurado.
    * El producto asociado al SKU está activo.
* **Simulación de Fulfillment:** La aplicación realiza una simulación de fulfillment utilizando el endpoint de VTEX para obtener el precio e inventario del SKU.
* **Almacenamiento en la Base de Datos:** La información de cada SKU se almacena o actualiza en la base de datos, garantizando que los registros reflejen los datos más recientes.
* **Registro de Logs:** Cada paso del proceso es registrado en el sistema de logs siguiendo los códigos de evento y mensajes estándar definidos por VTEX.

### Modelo de Datos para Productos
El modelo Product incluye los siguientes campos principales:

* `sku_id`: Identificador único del SKU en VTEX.
* `product_id`: Identificador único del producto en VTEX.
* `name`: Nombre del producto.
* `product_description`: Descripción del producto.
* `brand_name`: Nombre de la marca del producto.
* `category_id`: ID de la categoría del producto.
* `category_name`: Nombre de la categoría del producto.
* `image_url`: URL de la imagen del producto.
* `is_active`: Estado del SKU (1 = sí está activo; 0 = no está activo).
* `price`: Precio obtenido de la simulación.
* `inventory`: Nivel de inventario obtenido de la simulación.

### Endpoint para Carga Inicial de Productos
La aplicación expone un endpoint para iniciar el proceso de carga inicial:

Ruta: `/products/initial_load/`
Método: `POST`
Parámetro: `sales_channel_id` (ID del canal de ventas para el que se desea realizar la carga).

### Validación y Manejo de Errores
Si el SKU o el producto no cumplen con las validaciones, se registra un error y se continúa con el siguiente SKU.

## Notificaciones de Nuevos Productos o Actualizaciones desde VTEX
Además de la carga inicial de productos, la aplicación está preparada para recibir notificaciones desde VTEX cuando se crea o actualiza un producto o SKU.

### Proceso de Recepción de Notificaciones
* Cuando un nuevo producto o SKU se registra en VTEX, se envía una notificación al endpoint configurado.
* La aplicación procesa esta notificación para actualizar o registrar la información del producto en el marketplace.
* Se realizan las mismas validaciones que en la carga inicial, incluyendo la validación del estado del SKU, precio e inventario.

### Campos Recibidos en la Notificación
La notificación contiene los siguientes campos clave:

* `idSKU`: ID del SKU en VTEX.
* `productId`: ID del producto en VTEX.
* `an`: Nombre de la cuenta del seller en VTEX.
* `idAffiliate`: ID del afiliado generado automáticamente en la configuración.
* `DateModified`: Fecha de la última modificación del producto.
* `isActive`: Estado del producto (activo o inactivo).
* `StockModified`: Indica si el inventario ha sido modificado.
* `PriceModified`: Indica si el precio ha sido modificado.
* `HasStockKeepingUnitModified`: Indica si los datos del SKU han sido modificados.
* `HasStockKeepingUnitRemovedFromAffiliate`: Indica si el producto ya no está asociado con la política comercial.

### Registro de Logs
Cada notificación procesada genera un registro en el sistema de logs, donde se registra si la operación fue exitosa o si hubo algún error.

### Endpoint para Recibir Notificaciones: 
* Ruta: `/notifications/`
* Método: `POST`
* Descripción: Recibe notificaciones de VTEX sobre nuevos productos o actualizaciones de SKUs.

## Servicios de Ajuste de Precios e Inventario del Marketplace
Para simular comportamientos típicos de un marketplace, la aplicación incluye servicios que permiten ajustar los precios de los productos y gestionar inventario propio del marketplace.

### Funcionalidades Disponibles
* **Aplicar Interés a Precios**: Ajusta los precios de los productos aplicando un porcentaje de interés definido por el usuario.
* **Aplicar Descuento a Precios**: Aplica un porcentaje de descuento a los precios de los productos.
* **Aplicar Impuesto a Precios**: Ajusta los precios de los productos aplicando un porcentaje de impuesto definido.
* **Gestionar Inventario del Marketplace**: Permite establecer un inventario propio del marketplace para los SKUs.

### Endpoints Disponibles

#### 1. Aplicar Interés a Precios
* **Ruta**: `/adjustments/apply_interest`
* **Método**: `POST`
* **Descripción**: 
    * Aplica un porcentaje de interés a los precios de los SKUs especificados o a todos los SKUs si no se especifican.
    * La tasa debe ser un valor decimal entre 0 y 1.
    * Si `sku_ids` se omite, el interés se aplicará a todos los productos.

**Body de la Solicitud**:
```
{
  "rate": 0.05,          // Tasa de interés (ejemplo: 0.05 para 5%)
  "sku_ids": [100, 200]  // Opcional: Lista de SKU IDs a los que se aplicará el interés. Si se omite, se aplica a todos los SKUs.
}
```

#### 2. Aplicar Descuento a Precios
* **Ruta**: `/adjustments/apply_discount`
* **Método**: `POST`
* **Descripción**:  
    * Aplica un porcentaje de descuento a los precios de los SKUs especificados o a todos los SKUs si no se especifican.
    * La tasa debe ser un valor decimal entre 0 y 1.
    * Si `sku_ids` se omite, el interés se aplicará a todos los productos.

**Body de la Solicitud**:
```
{
  "rate": 0.10,          // Tasa de descuento (ejemplo: 0.10 para 10%)
  "sku_ids": [100, 200]  // Opcional: Lista de SKU IDs a los que se aplicará el descuento. Si se omite, se aplica a todos los SKUs.
}

```

#### 3. Aplicar Impuesto a Precios
* **Ruta**: `/adjustments/apply_tax`
* **Método**: `POST`
* **Descripción**:   
    * Aplica un porcentaje de impuesto a los precios de los SKUs especificados o a todos los SKUs si no se especifican.
    * La tasa debe ser un valor decimal entre 0 y 1.
    * Si `sku_ids` se omite, el interés se aplicará a todos los productos.

**Body de la Solicitud**:
```
{
  "rate": 0.08,          // Tasa de impuesto (ejemplo: 0.08 para 8%)
  "sku_ids": [100, 200]  // Opcional: Lista de SKU IDs a los que se aplicará el impuesto. Si se omite, se aplica a todos los SKUs.
}
```

#### 4. Establecer Inventario del Marketplace
* **Ruta**: `/adjustments/set_marketplace_inventory`
* **Método**: `POST`
* **Descripción**:  
    * Establece el inventario propio del marketplace para un SKU específico.
    * Solo se puede actualizar un SKU por solicitud.
    * El inventario debe ser un número entero positivo.

**Body de la Solicitud**:
```
{
  "sku_id": 100,         // ID del SKU al que se le establecerá el inventario.
  "inventory": 50       // Cantidad de inventario a establecer.
}
```