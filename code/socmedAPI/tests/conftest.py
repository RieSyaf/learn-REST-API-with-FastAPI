import os
from typing import Generator, AsyncGenerator
import pytest

from fastapi.testclient import TestClient
from httpx import AsyncClient

from socmedAPI.routers.post import post_table, comment_table

os.environ["ENV_STATE"] = "test"

from socmedAPI.main import app #noqa: E402

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)

@pytest.fixture(autouse=True)
def db() -> Generator:
    post_table.clear()
    comment_table.clear()
    yield
    post_table.clear()
    comment_table.clear()



@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac