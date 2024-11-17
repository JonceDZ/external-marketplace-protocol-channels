# app/main.py

from fastapi import FastAPI
from app.api.routes import notifications, ui, logs, products, orders
from app.db.database import create_database

# Crear la base de datos al iniciar
create_database()

app = FastAPI(title="VTEX External Marketplace Integration")

# Incluir rutas
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(ui.router, tags=["UI"])
app.include_router(logs.router, tags=["Logs"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])

# Montar archivos estáticos
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="app/static"), name="static")