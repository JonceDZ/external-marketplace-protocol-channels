from fastapi import FastAPI
from app.api.routes import notifications, ui, logs  # Importa los módulos de rutas notifications y ui

app = FastAPI(title="VTEX External Marketplace Integration") # Definición de la instancia principal.

# Crear la base de datos al iniciar
#create_database()

# Incluir rutas
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"]) # El prefix es el trozo de path que se agregaría a la ruta a la cual estamos redireccionando el request
app.include_router(ui.router, tags=["UI"])
app.include_router(logs.router, tags=["Logs"])  # Incluir el router de logs

# Punto de entrada de la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)