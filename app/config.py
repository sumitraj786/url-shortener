from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./url_shortener.db"
    base_url: str = "http://localhost:8000"
    short_code_length: int = 6
    rate_limit_per_minute: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
