import pytest

from accounts.entrypoints.sanic_app.status_codes import StatusCodes
from e2e.api.v1.api_client import (
    delete_user,
    get_users,
    post_auth,
    post_create_user,
    put_user,
)


@pytest.fixture
async def admin_token(test_client, admin_user):
    """Фикстура для получения токена администратора"""
    request, response = await post_auth(test_client, admin_user.email, "admin_pass")
    return response.json["access_token"]


@pytest.mark.asyncio
async def test_admin_create_user(test_client, admin_token):
    new_email = "new_user@example.com"
    request, response = await post_create_user(
        test_client,
        token=admin_token,
        email=new_email,
        full_name="New Guy",
        password="securepass",
    )

    assert response.status_code == StatusCodes.SUCCESS_CREATED
    assert response.json["status"] == "success"


@pytest.mark.asyncio
async def test_admin_get_users(test_client, admin_token):
    request, response = await get_users(test_client, admin_token)

    assert response.status_code == StatusCodes.SUCCESS
    assert isinstance(response.json["users"], list)
    assert len(response.json["users"]) >= 1  # Как минимум сам админ там есть


@pytest.mark.asyncio
async def test_admin_update_user(test_client, admin_token, regular_user):
    """
    Тест обновления пользователя.
    Используем прямой вызов client.post, так как в helpers.py функция patch_user
    использует метод PATCH, а в роутере прописан POST.
    """
    user_id = regular_user.user_id

    email = "updated@example.com"
    full_name = "Updated Name"
    password = "newpassword123"

    request, response = await put_user(
        user_id=user_id,
        email=email,
        full_name=full_name,
        password=password,
        token=admin_token,
        test_client=test_client,
    )

    assert response.status_code == StatusCodes.SUCCESS_NO_CONTENT

    # Проверка (можно сделать логин с новым паролем или get_users)


@pytest.mark.asyncio
async def test_admin_delete_user(test_client, admin_token):
    # Сначала создаем временного юзера, чтобы не ломать других
    request_post_create_user, response_post_create_user = await post_create_user(
        test_client, admin_token, "todelete@ex.com", "Temp", "123"
    )

    # Предполагаем, что нам нужно получить ID созданного юзера.
    # Если create_user не возвращает ID, придется найти его через get_users
    # Для теста допустим, мы нашли ID:
    request_get_users, response_get_users = await get_users(test_client, admin_token)
    target_user = next(
        u for u in response_get_users.json["users"] if u["email"] == "todelete@ex.com"
    )
    target_id = target_user["user_id"]

    request_delete_user, response_delete_user = await delete_user(
        test_client, admin_token, target_id
    )
    assert response_delete_user.status_code == StatusCodes.SUCCESS_NO_CONTENT
