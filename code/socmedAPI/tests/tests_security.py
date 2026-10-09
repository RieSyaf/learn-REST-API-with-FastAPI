import pytest
from socmedAPI import security


@pytest.mark.asyncio
asynd def test_get_user(registered_user: dict):
    user await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]

@pytest.mark.asyncio
async def test_get_user_not_found():
    user = await security.get_user("test@exaple.com")
    assert user is None