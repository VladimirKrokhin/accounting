class TestUserMe:
    def test_get_my_profile_success(self, test_client, setup_uow):
        """Получение данных профиля авторизованным пользователем"""
        raise NotImplementedError

    def test_get_my_accounts_and_balances(self, test_client, setup_uow):
        """Проверка списка счетов текущего пользователя"""
        raise NotImplementedError

    def test_get_my_payments_history(self, test_client, setup_uow):
        """Проверка истории платежей текущего пользователя"""
        raise NotImplementedError

    def test_unauthorized_access_denied(self, test_client):
        """Проверка защиты эндпоинтов (401 error без токена)"""
        raise NotImplementedError
