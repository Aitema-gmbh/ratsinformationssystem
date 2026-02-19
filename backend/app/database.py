"""
Database configuration for aitema|Rats

PostgreSQL with schema-per-tenant isolation.
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aitema:aitema@localhost:5432/ris")

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session():
    """Context manager for background tasks."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def set_tenant_schema(session: Session, tenant_schema: str):
    """Set the search path to a tenant-specific schema."""
    session.execute(text(f"SET search_path TO {tenant_schema}, public"))


def create_tenant_schema(tenant_id: str):
    """Create a new schema for a tenant."""
    schema_name = f"tenant_{tenant_id}"
    with get_session() as session:
        session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        # Create all tables in the tenant schema
        session.execute(text(f"SET search_path TO {schema_name}, public"))
        Base.metadata.create_all(bind=session.get_bind())
    return schema_name


def init_db():
    """Initialize the database with all tables."""
    Base.metadata.create_all(bind=engine)
