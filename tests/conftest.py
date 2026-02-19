"""
aitema|RIS - Test Configuration
Shared fixtures for all tests.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings
from app.core.database import Base, get_db
from app.main import app


# Override settings for testing
def get_test_settings() -> Settings:
    return Settings(
        database_url="postgresql+asyncpg://ris:ris_dev_password@localhost:5432/ris_test",
        redis_url="redis://:redis_dev_password@localhost:6379/1",
        elasticsearch_url="http://localhost:9200",
        environment="development",
        secret_key="test-secret-key-not-for-production",
    )


test_settings = get_test_settings()

test_engine = create_async_engine(
    test_settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

test_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create test database tables once per session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for each test."""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers() -> dict[str, str]:
    """Provide authentication headers with a test JWT."""
    from jose import jwt

    payload = {
        "sub": str(uuid.uuid4()),
        "email": "test@example.de",
        "name": "Test User",
        "preferred_username": "testuser",
        "realm_access": {"roles": ["admin", "sitzungsdienst"]},
        "tenant_id": "test-kommune",
    }
    token = jwt.encode(payload, test_settings.secret_key, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_system(db_session: AsyncSession):
    """Create a sample OParl System for testing."""
    from app.models.oparl import System

    system = System(
        oparl_type="https://schema.oparl.org/1.1/System",
        oparl_version="https://schema.oparl.org/1.1/",
        name="Test RIS System",
        contact_email="test@example.de",
        vendor="https://aitema.de",
        product="https://aitema.de/ris",
    )
    db_session.add(system)
    await db_session.flush()
    return system


@pytest_asyncio.fixture
async def sample_body(db_session: AsyncSession, sample_system):
    """Create a sample OParl Body for testing."""
    from app.models.oparl import Body

    body = Body(
        oparl_type="https://schema.oparl.org/1.1/Body",
        system_id=sample_system.id,
        name="Teststadt",
        short_name="TST",
        ags="12345678",
        classification="Stadt",
        contact_email="rat@teststadt.de",
    )
    db_session.add(body)
    await db_session.flush()
    return body
