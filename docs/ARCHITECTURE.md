# Arquitectura del Proyecto: VTEX External Marketplace Integration

## Descripción General
El fin de este desarrollo es ofrecer una aplicación que permita a los VTEXers entender la manera en cómo opera una integración basada en el External Marketplace Protocol. Se denomina transparente, ya que busca ofrecer la perspectiva de ambos lados, tanto desde el seller VTEX, como del Marketplace externo.

## Tecnologías y Herramientas Utilizadas
- **Lenguaje de Programación:** Python 3.9.6
- **Framework Backend:** FastAPI
- **Interfaz de Usuario:** Jinja2 (con posibilidad de utilizar Vue.js en el futuro)
- **Base de Datos:** SQLite (con posibilidad de migrar a PostgreSQL)
- **ORM:** SQLAlchemy
- **Validación de Datos:** Pydantic
- **Servidor ASGI:** Uvicorn
- **Manejo de Variables de Entorno:** python-dotenv
- **Cliente HTTP para VTEX:** requests
- **Control de Versiones:** Git (repositorio en GitHub)
- **Gestión de Dependencias:** pip y requirements.txt
- **Entorno Virtual:** conda

## Estructura de Directorios
La estructura general del proyecto es la siguiente:

external-marketplace-protocol-channels/
├── app/
│   ├── main.py                   # Punto de entrada de la aplicación
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── notifications.py   # Módulo para manejar notificaciones
│   │       ├── logs.py            # Módulo para obtener los logs
│   │       └── ui.py              # Módulo para manejar la interfaz de usuario
│   │
│   ├── config/
│   │   └── settings.py            # Configuración y manejo de variables de entorno
│   │
│   ├── db/
│   │   └── database.py            # Configuración y conexión de la base de datos
│   │
│   ├── models/
│   │   ├── schemas/               # Esquemas de validación y estructura de datos
│   │   │   ├── brand_schema.py    # Esquema para datos de marcas
│   │   │   ├── category_schema.py # Esquema para datos de categorías
│   │   │   ├── inventory_schema.py# Esquema para datos de inventario
│   │   │   ├── order_schema.py    # Esquema para datos de pedidos
│   │   │   └── product_schema.py  # Esquema para datos de productos
│   │   └── database_models.py     # Definición de modelos de la base de datos
│   │
│   ├── services/
│   │   ├── brand_service.py       # Lógica de negocio para marcas
│   │   ├── category_service.py    # Lógica de negocio para categorías
│   │   ├── inventory_service.py   # Lógica de negocio para inventario
│   │   ├── order_service.py       # Lógica de negocio para pedidos
│   │   ├── product_service.py     # Lógica de negocio para productos
│   │   └── vtex_api.py            # Servicio para integración con VTEX
│   │
│   ├── static/                    # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/                   # Archivos de estilos CSS
│   │   ├── images/                # Imágenes utilizadas en la aplicación
│   │   └── js/                    # Archivos JavaScript
│   │
│   ├── templates/                 # Plantillas HTML para la interfaz de usuario
│   │   ├── base.html              # Plantilla base
│   │   ├── index.html             # Página principal
│   │   ├── orders.html            # Página para visualizar pedidos
│   │   └── products.html          # Página para visualizar productos
│   │
│   └── utils/
│       ├── error_handling.py      # Módulo para manejo de errores
│       └── logging.py             # Configuración de logging para la aplicación
│   
├── docs/
│   ├── ARCHITECTURE.md            # Documentación de la arquitectura del proyecto
│   └── README.md                  # Documentación general del proyecto
│   
├── tests/                         # Pruebas unitarias y de integración
│   ├── test_app.py                # Pruebas para la aplicación principal
│   └── test_env.py                # Pruebas para el entorno y configuración
│   
├── .env                           # Variables de entorno (no se sube al repositorio)
│   
├── .gitignore                     # Archivos y directorios que deben ser ignorados por Git
│   
└── requirements.txt               # Lista de dependencias del proyecto


## Flujos de Datos
1. **Obtención de Información desde VTEX:**
   - La aplicación realiza solicitudes HTTP a VTEX para obtener datos como productos, categorías y marcas.
   - Estos datos se almacenan localmente en la base de datos SQLite para su uso y visualización.

2. **Notificaciones desde VTEX:**
   - La aplicación recibe notificaciones desde VTEX cuando hay actualizaciones en el catálogo de productos.
   - Estas notificaciones son procesadas y actualizan los registros en la base de datos.

3. **Interacción con la Interfaz de Usuario:**
   - Los usuarios pueden visualizar los productos y órdenes a través de la interfaz web.
   - La UI interactúa con los servicios internos de la aplicación para obtener y mostrar la información.

## Manejo de Variables de Entorno
Las variables de entorno sensibles (como las credenciales de VTEX) se almacenan en un archivo `.env` que no se sube al repositorio por seguridad. Estas variables se cargan mediante `python-dotenv` y se manejan en el archivo `settings.py`.

## Buenas Prácticas de Seguridad
- Validar que las solicitudes a VTEX incluyen las credenciales necesarias.
- Implementar medidas de seguridad para el endpoint de notificaciones, como la validación del origen de las solicitudes.

## Próximos Pasos
- Implementar la lógica de negocio y la integración completa con la API de VTEX.
- Desarrollar la interfaz de usuario y permitir la interacción con los datos integrados.
