from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ttl: int = 300
    bls_api_key: str | None = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
