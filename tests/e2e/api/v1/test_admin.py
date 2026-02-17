# import pytest
# from accounts.entrypoints.sanic_app.status_codes import StatusCodes
# from accounts.views import get_users
# from e2e.api.v1.api_client import delete_user, post_auth, post_create_user
#
#
# @pytest.fixture
# def admin_token(test_client, admin_user_data):
#     """Фикстура для получения токена администратора"""
#     _, body = post_auth(
#         test_client, admin_user_data["email"], admin_user_data["password"]
#     )
#     return body["access_token"]
#
#
# def test_admin_create_user(test_client, admin_token):
#     new_email = "new_user@example.com"
#     status, body = post_create_user(
#         test_client,
#         token=admin_token,
#         email=new_email,
#         full_name="New Guy",
#         password="securepass",
#     )
#
#     assert status == StatusCodes.SUCCESS_CREATED
#     assert body["status"] == "success"
#
#
# def test_admin_get_users(test_client, admin_token):
#     status, body = get_users(test_client, admin_token)
#
#     assert status == StatusCodes.SUCCESS
#     assert isinstance(body["users"], list)
#     assert len(body["users"]) >= 1  # Как минимум сам админ там есть
#
#
# def test_admin_update_user(test_client, admin_token, regular_user_data):
#     """
#     Тест обновления пользователя.
#     Используем прямой вызов client.post, так как в helpers.py функция patch_user
#     использует метод PATCH, а в роутере прописан POST.
#     """
#     user_id = regular_user_data["id"]
#     update_url = f"/api/v1/users/{user_id}"
#
#     payload = {
#         "email": "updated@example.com",
#         "full_name": "Updated Name",
#         "password": "newpassword123",
#     }
#
#     request, response = test_client.post(
#         update_url, json=payload, headers={"Authorization": f"Bearer {admin_token}"}
#     )
#
#     assert response.status == StatusCodes.SUCCESS_NO_CONTENT
#
#     # Проверка (можно сделать логин с новым паролем или get_users)
#
#
# def test_admin_delete_user(test_client, admin_token):
#     # Сначала создаем временного юзера, чтобы не ломать других
#     _, create_body = post_create_user(
#         test_client, admin_token, "todelete@ex.com", "Temp", "123"
#     )
#
#     # Предполагаем, что нам нужно получить ID созданного юзера.
#     # Если create_user не возвращает ID, придется найти его через get_users
#     # Для теста допустим, мы нашли ID:
#     status_get, body_get = get_users(test_client, admin_token)
#     target_user = next(u for u in body_get["users"] if u["email"] == "todelete@ex.com")
#     target_id = target_user["id"]
#
#     status, _ = delete_user(test_client, admin_token, target_id)
#     assert status == StatusCodes.SUCCESS_NO_CONTENT
