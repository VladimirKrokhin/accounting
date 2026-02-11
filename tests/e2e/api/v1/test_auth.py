import pytest


class TestAuth:
    def test_login_success(self, test_client, setup_uow):
        """Тест успешного входа и получения токена"""
        raise NotImplementedError

    def test_login_invalid_credentials(self, test_client, setup_uow):
        """Тест ошибки авторизации (неверный пароль/email)"""
        raise NotImplementedError
