from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    vtex_app_key: str
    vtex_app_token: str
    vtex_account_name: str
    vtex_api_url: str
    sales_channel_id: int

    class Config:
        env_file = ".env" # Especifica que las variables se tomarán del archivo .env

settings = Settings()