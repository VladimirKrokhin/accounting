import pytest
from e2e.api.v1.api_client import post_auth


@pytest.mark.asyncio
async def test_login_fail_user_not_found(test_client):
    request, response = await post_auth(test_client, "ghost@example.com", "123456")

    assert response.status_code == 401
