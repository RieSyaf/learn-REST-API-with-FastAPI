import httpx
import pytest

from databases import Database
from socmedAPI.database import post_table, database
from socmedAPI.tasks import APIResponseError,  _generate_cute_creature_api, generate_and_add_to_post



@pytest.mark.anyio
async def test_generate_cute_creature_api_success(mock_httpx_client):
    json_data = {"output_url": "httpx://example.com/image.jpg"}

    mock_httpx_client.post.return_value = httpx.Response(
        status_code=200, json=json_data, request=httpx.Request("POST", "//")
    )

    result = await _generate_cute_creature_api("A cat")

    assert result == json_data

@pytest.mark.anyio
async def test_generate_cute_creature_api_server_error(mock_httpx_client):

    mock_httpx_client.post.return_value = httpx.Response(
        status_code=500, content="", request=httpx.Request("POST", "//")
    )

    with pytest.raises(
        APIResponseError,
        match="API request failed with status code 500"
    ):
        await _generate_cute_creature_api("A cat")


@pytest.mark.anyio
async def test_generate_cute_creature_api_json_error(mock_httpx_client):

    mock_httpx_client.post.return_value = httpx.Response(
        status_code=200, content="Not JSON", request=httpx.Request("POST", "//")
    )

    with pytest.raises(
        APIResponseError,
        match="API response parsing failed"
    ):
        await _generate_cute_creature_api("A cat")


@pytest.mark.anyio
async def test_generate_and_add_to_post_success(
    mock_httpx_client, user_for_tasks: dict
):
    json_data = {"output_url": "httpx://example.com/image.jpg"}

    mock_httpx_client.post.return_value = httpx.Response(
        status_code=200, json=json_data, request=httpx.Request("POST", "//")
    )

    query = post_table.insert().values(
        user_id=user_for_tasks["id"],
        body="Test post"
    )
    post_id = await database.execute(query)

    await generate_and_add_to_post(
        user_for_tasks["email"],
        post_id,
        "/post/1",
        database,
        "A cat"
    )

    query = post_table.select().where(post_table.c.id == post_id)

    updated_post = await database.fetch_one(query)

    assert updated_post["image_url"] == json_data["output_url"]