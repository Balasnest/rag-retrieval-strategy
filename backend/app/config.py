"""
Central app configuration, read from environment variables (set via
docker-compose.yml, or a local .env when running outside Docker).
"""
import os


class Settings:
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://rag:rag@localhost:5432/rag_explorer"
    )
    elasticsearch_url: str = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    openai_embedding_model: str = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_chat_model: str = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4.1")
    cors_origins: list[str] = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()
