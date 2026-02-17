# import pytest
# from accounts.entrypoints.sanic_app.status_codes import StatusCodes
# from .api_client import (
#     post_auth,
#     get_current_user,
#     get_current_user_accounts,
#     get_current_user_payments,
# )
#
#
# @pytest.fixture
# def user_token(test_client, regular_user_data):
#     """Фикстура для получения токена перед тестами"""
#     _, body = post_auth(
#         test_client, regular_user_data["email"], regular_user_data["password"]
#     )
#     return body["access_token"]
#
#
# def test_get_me_success(test_client, user_token, regular_user_data):
#     status, body = get_current_user(test_client, user_token)
#
#     assert status == StatusCodes.SUCCESS
#     assert body["user"]["email"] == regular_user_data["email"]
#     # Пароль (хэш) не должен возвращаться в ответе
#     assert "password" not in body["user"]
#     assert "password_hash" not in body["user"]
#
#
# def test_get_my_accounts(test_client, user_token):
#     status, body = get_current_user_accounts(test_client, user_token)
#
#     assert status == StatusCodes.SUCCESS
#     assert isinstance(body["user"]["accounts"], list)
#     # Если у юзера при создании был счет, проверяем его наличие
#     # assert len(body["user"]["accounts"]) > 0
#
#
# def test_get_me_unauthorized(test_client):
#     """Проверка доступа без токена"""
#     # Вызываем напрямую через клиент, так как хелпер требует токен
#     request, response = test_client.get("/api/v1/users/me")
#     assert response.status == 401  # Стандартный код Sanic/JWT для отсутствия auth
