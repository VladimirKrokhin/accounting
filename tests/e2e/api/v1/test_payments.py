# import pytest
# import hashlib
# from uuid import uuid4
# from accounts.entrypoints.sanic_app.status_codes import StatusCodes
# from e2e.api.v1.api_client import post_transaction
#
#
# def test_webhook_transaction_success(test_client, regular_user_data, sanic_app):
#     # 1. Подготовка данных
#     secret = sanic_app.config.PAYMENT_SYSTEM_SECRET_KEY
#     t_id = str(uuid4())
#     user_id = regular_user_data["id"]  # Предполагаем, что фикстура возвращает ID
#     account_id = 1  # Предполагаем, что счет 1 существует
#     amount = 100.0
#
#     params = {
#         "transaction_id": t_id,
#         "user_id": user_id,
#         "account_id": account_id,
#         "amount": amount,
#     }
#
#     signature = "..."
#
#     # 3. Отправка вебхука
#     status, body = post_transaction(
#         test_client,
#         transaction_id=t_id,
#         account_id=account_id,
#         user_id=user_id,
#         amount=amount,
#         signature=signature,
#     )
#
#     assert status == StatusCodes.SUCCESS_CREATED
#     assert body["status"] == "success"
#
#
# def test_webhook_invalid_signature(test_client, regular_user_data):
#     status, body = post_transaction(
#         test_client,
#         transaction_id=str(uuid4()),
#         account_id=1,
#         user_id=regular_user_data["id"],
#         amount=100,
#         signature="fake_signature_123",
#     )
#
#     assert status == StatusCodes.ERROR_UNPROCESSABLE_ENTITY
#     assert body["message"] == "signature is not valid"
