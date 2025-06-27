from pydantic import BaseSettings

class Settings(BaseSettings):
    ttl: int = 300

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
