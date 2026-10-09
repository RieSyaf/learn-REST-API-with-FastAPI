import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import anyio
import httpx

from fastapi.testclient import TestClient
from httpx import AsyncClient

import os
os.environ["ENV_STATE"] = "test"

from socmedAPI.database import database, post_table, comment_table, user_table
from socmedAPI.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> pytest.fixture:
    yield TestClient(app)


@pytest.fixture(autouse=True)
def db() -> pytest.fixture:
    async def clear_db():
        await database.execute(post_table.delete())
        await database.execute(comment_table.delete())
    
    anyio.run(clear_db)
    yield
    anyio.run(clear_db)


@pytest.fixture()
async def async_client(client) -> pytest.fixture:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac