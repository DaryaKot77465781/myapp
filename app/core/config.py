from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'Career Growth MVP'
    database_url: str = 'postgresql+psycopg://app:app@localhost:5432/career'
    redis_url: str = 'redis://localhost:6379/0'
    qdrant_url: str = 'http://localhost:6333'
    api_key: str = 'dev-api-key'
    qdrant_collection_learning: str = 'learning_items'
    qdrant_collection_skills: str = 'skills'


settings = Settings()
