import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from app.app import app
from app.modules.db import Database



@pytest.fixture
def mock_db():
    db = AsyncMock(spec=Database)
    db.fetchone = AsyncMock()
    db.fetch = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
async def async_client(mock_db):
    app.state.db_client = mock_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac
