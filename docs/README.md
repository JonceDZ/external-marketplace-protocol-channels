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

### Cómo Ejecutar el Proyecto
1. Inicia el servidor FastAPI: `uvicorn app.main:app --reload`

2. Accede a la aplicación en tu navegador: http://127.0.0.1:8000
Para ver la documentación interactiva generada por FastAPI, visita: http://127.0.0.1:8000/docs

### Estructura del Proyecto
La estructura del proyecto se ha detallado en ARCHITECTURE.md. Consulta ese archivo para entender cómo está organizada la aplicación y cómo se integran los diferentes componentes.

### Próximos Pasos
1. Implementar la lógica de negocio completa para la integración con VTEX.
2. Desarrollar y mejorar la interfaz de usuario.
3. Realizar pruebas unitarias e integrales para garantizar la funcionalidad de la aplicación.