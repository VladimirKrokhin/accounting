from adapters.auth import generate_password_hash
from dtos import UserDTO, UserType
from domain.types import UserId
from e2e.api.v1.api_client import get_user_accounts, post_auth, post_transaction


class TestPayments:
    def test_webhook_transaction_created_successfully(self, test_client, sanic_app):
        """Успешная обработка вебхука и обновление баланса"""

        uow = sanic_app.ctx.message_bus.uow
        # 1. Предусловие: создаем юзера в БД
        with uow:
            account_id = 1
            user_id = UserId(1)
            user = UserDTO(
                user_id=UserId(1),
                email="customer@test.com",
                full_name="Customer",
                user_type=UserType.USER,
                password_hash="password_hash",
            )
            uow.users.save_user(user)

            admin_email = "admin@example.com"
            admin_pass = "admin"
            admin = UserDTO(
                user_id=UserId(2),
                email=admin_email,
                full_name="Admin",
                user_type=UserType.ADMIN,
                password_hash=generate_password_hash(admin_pass),
            )
            uow.users.save_user(admin)
            uow.commit()

        with uow:
            # 2. Данные вебхука (подпись должна генерироваться как в платежке)
            transaction_id = "5eae174f-7cd0-472c-bd36-35660f00132b"
            user_id = user_id
            account_id = account_id
            amount = 100
            signature = (
                "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
            )

            # 3. Действие: вызываем эндпоинт транзакций
            status, json = post_transaction(
                sanic_test_client=test_client,
                transaction_id=transaction_id,
                account_id=account_id,
                user_id=user_id,
                amount=amount,
                signature=signature,
            )

            # 4. Проверка
            assert status == 201
            uow.commit()

            status, auth_res = post_auth(
                email=admin_email, password=admin_pass, sanic_test_client=test_client
            )
            assert status == 200

            token = auth_res["access_token"]
            status, json = get_user_accounts(
                sanic_test_client=test_client,
                token=token,
                user_id=user_id,
            )
            assert status == 200

            user_accounts = json
            raise Exception(user_accounts)
            assert user_accounts["user"][0]["balance"] == 100

    def test_webhook_invalid_signature_error(self, test_client, setup_uow):
        """Ошибка при невалидной подписи платежной системы"""
        raise NotImplementedError

    def test_webhook_duplicate_transaction_conflict(self, test_client, setup_uow):
        """Ошибка при попытке обработать транзакцию, которая уже есть в базе"""
        raise NotImplementedError

    def test_webhook_user_not_found(self, test_client, setup_uow):
        """Обработка платежа для несуществующего пользователя"""
        raise NotImplementedError
