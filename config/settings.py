from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    agent_api_key: str = "mock"
    venue_id: str = "venue-001"
    venue_name: str = "MetroArena"
    app_port: int = 8000
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
