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
async def db() -> pytest.fixture:
    async def clear_db():
        await database.execute(post_table.delete())
        await database.execute(comment_table.delete())
        await database.execute(user_table.delete())
    
    await clear_db()
    yield
    await clear_db()


@pytest.fixture()
async def async_client(client) -> pytest.fixture:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.com", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user["id"]
    return user_details