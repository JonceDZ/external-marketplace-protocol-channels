from fastapi import FastAPI
from app.api.routes import notifications, ui  # Importa los módulos de rutas notifications y ui

app = FastAPI(title="VTEX External Marketplace Integration") # Definición de la instancia principal.

# Incluir rutas (actualizaremos estas rutas más adelante cuando los archivos estén listos)
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(ui.router, tags=["UI"])

# Punto de entrada de la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)