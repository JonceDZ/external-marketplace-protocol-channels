from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    vtex_app_key: str
    vtex_app_token: str
    vtex_account_name: str
    vtex_api_url: str

    class Config:
        env_file = ".env"

settings = Settings()