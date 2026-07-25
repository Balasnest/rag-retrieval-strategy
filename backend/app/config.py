import os


class Settings:
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://rag:rag@localhost:5432/rag_explorer"
    )
    elasticsearch_url: str = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    claude_model: str = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    cors_origins: list[str] = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()
