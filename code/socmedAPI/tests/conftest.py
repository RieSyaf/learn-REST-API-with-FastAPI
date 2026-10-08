import os
from typing import Generator, AsyncGenerator
import pytest
import anyio

from fastapi.testclient import TestClient
import httpx

os.environ["ENV_STATE"] = "test"

from socmedAPI.database import database, post_table, comment_table
from socmedAPI.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
def db() -> Generator:
    async def clear_db():
        await database.execute(post_table.delete())
        await database.execute(comment_table.delete())
    
    anyio.run(clear_db)
    yield
    anyio.run(clear_db)


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac