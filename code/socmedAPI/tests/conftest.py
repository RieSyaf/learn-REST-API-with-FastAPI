import os
from collections.abc import AsyncGenerator, Generator

import anyio
import httpx
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


os.environ["ENV_STATE"] = "test"

from socmedAPI.database import comment_table, database, post_table, user_table
from socmedAPI.main import app
from socmedAPI.tests.helpers import create_post 


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
        await database.execute(user_table.delete())
        from socmedAPI.database import like_table
        await database.execute(like_table.delete())

    anyio.run(clear_db)
    yield
    anyio.run(clear_db)


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.com", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user["id"]
    return user_details

@pytest.fixture()
async def confirmed_user(registered_user: dict) -> dict:

    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    response = await async_client.post(
        "/token",
        data={"username": confirmed_user["email"], "password": confirmed_user["password"]},
    )
    return response.json()["access_token"]


@pytest.fixture()
def mock_httpx_client(mocker):
    mock = mocker.patch("socmedAPI.tasks.httpx.AsyncClient", autospec=True)
    mock.return_value.__aenter__.return_value = mock.return_value
    return mock.return_value


@pytest.fixture()
async def user_for_tasks(mock_httpx_client):
    user_details = {"email": "tasktest@example.com", "password": "1234", "id": 1}
    query = user_table.insert().values(
        email=user_details["email"],
        password=user_details["password"],
        confirmed=True
    )
    user_id = await database.execute(query)
    user_details["id"] = user_id
    return user_details



@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return await create_post("Test post", async_client, logged_in_token)
