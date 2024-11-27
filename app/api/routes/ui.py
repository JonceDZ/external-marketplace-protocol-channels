from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.database_models import Product
from app.services.product_service import process_initial_load
from app.config.settings import settings
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def check_database_empty():
    try:
        db: Session = SessionLocal()
        product_count = db.query(Product).count()
        db.close()
        print(f"Cantidad de productos en la base de datos: {product_count}")
        return product_count == 0
    except Exception as e:
        print(f"Error al comprobar la base de datos: {e}")
        return True

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if check_database_empty():
        return templates.TemplateResponse("index.html", {"request": request, "title": "Configuración Inicial"})
    else:
        return RedirectResponse(url="/products")

@router.post("/", response_class=HTMLResponse)
async def initial_setup(
    request: Request,
    vtex_app_key: str = Form(...),
    vtex_app_token: str = Form(...),
    vtex_account_name: str = Form(...),
    sales_channel_id: int = Form(...)
):
    # Actualizar el archivo .env
    update_env_file(
        vtex_app_key=vtex_app_key,
        vtex_app_token=vtex_app_token,
        vtex_account_name=vtex_account_name,
        vtex_api_url=f"https://{vtex_account_name}.vtexcommercestable.com.br/api",
        sales_channel_id=sales_channel_id
    )
    # Recargar la configuración
    settings.reload()

    # Iniciar la carga inicial del catálogo
    try:
        process_initial_load(sales_channel_id)
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "message": str(e)})
    return RedirectResponse(url="/products", status_code=303)

@router.get("/products", response_class=HTMLResponse)
async def show_products(request: Request):
    db: Session = SessionLocal()
    products = db.query(Product).filter(Product.is_active == True).all()
    db.close()
    return templates.TemplateResponse("products.html", {"request": request, "title": "Productos", "products": products})

def update_env_file(**kwargs):
    env_file_path = os.path.join(os.getcwd(), '.env')
    env_vars = {}
    # Leer las variables existentes
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    # Actualizar con las nuevas variables
    env_vars.update(kwargs)
    # Escribir las variables al archivo
    with open(env_file_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

def update_env_file(**kwargs):
    env_file_path = os.path.join(os.getcwd(), '.env')
    # Escribir las variables al archivo, sobreescribiendo el contenido previo
    with open(env_file_path, 'w') as f:
        for key, value in kwargs.items():
            f.write(f"{key}={value}\n")

@router.get("/orders", response_class=HTMLResponse)
async def show_orders(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request, "title": "Órdenes"})

@router.get("/notifications", response_class=HTMLResponse)
async def show_notifications(request: Request):
    return templates.TemplateResponse("notifications.html", {"request": request, "title": "Notificaciones"})