from pathlib import Path

from pydantic_settings import BaseSettings

# .env in project root (one level up from backend/app)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "supplymap-dev"

    class Config:
        env_prefix = "NEO4J_"
        env_file = _env_path
        extra = "ignore"
        env_file_encoding = "utf-8"


settings = Settings()
