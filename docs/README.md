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
* `name`: Nombre del producto.
* `is_active`: Estado del SKU.
* `price`: Precio obtenido de la simulación.
* `inventory`: Nivel de inventario obtenido de la simulación.

### Endpoint para Carga Inicial de Productos
La aplicación expone un endpoint para iniciar el proceso de carga inicial:

Ruta: `/products/initial_load/`
Método: `POST`
Parámetro: `sales_channel_id` (ID del canal de ventas para el que se desea realizar la carga).

### Validación y Manejo de Errores
Si el SKU o el producto no cumplen con las validaciones, se registra un error y se continúa con el siguiente SKU.