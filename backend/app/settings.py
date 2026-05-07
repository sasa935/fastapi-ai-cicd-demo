from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./shortlink.db"
    base_url: str = "http://localhost:8000"
    code_length: int = 7


settings = Settings()
