from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    vtex_app_key: Optional[str] = None
    vtex_app_token: Optional[str] = None
    vtex_account_name: Optional[str] = None
    vtex_api_url: Optional[str] = None
    sales_channel_id: Optional[int] = None

    class Config:
        env_file = ".env"  # Especifica que las variables se tomarán del archivo .env

    def reload(self):
        # Forzar la recarga de las variables de entorno
        self.__dict__.update(self.__class__().dict())

settings = Settings()
