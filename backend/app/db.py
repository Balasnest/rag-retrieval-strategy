"""
SQLAlchemy engine + session factory.

NOTE (Phase 1): nothing in this phase actually queries the database yet
- `create_engine` doesn't open a connection until first use, so the API
can boot and serve requests even if Postgres isn't running. Real usage
starts in Phase 2 (document/chunk models) and Phase 3 (pgvector search).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
