import os


class Settings:
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://rag:rag@localhost:5432/rag_explorer"
    )
    elasticsearch_url: str = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")

    # LLM provider — set to "anthropic" or "openai"
    llm_provider: str = os.environ.get("LLM_PROVIDER", "anthropic")

    # Anthropic
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    claude_model: str = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

    # OpenAI
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    openai_chat_model: str = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    # Embeddings — sentence-transformers model (runs locally, no API key needed)
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    cors_origins: list[str] = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()
