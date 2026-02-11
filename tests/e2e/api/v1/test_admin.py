class TestAdmin:
    def test_admin_creates_new_user(self, test_client, setup_uow):
        """Админ успешно создает нового пользователя"""
        raise NotImplementedError

    def test_admin_updates_user_info(self, test_client, setup_uow):
        """Админ успешно обновляет данные существующего пользователя"""
        raise NotImplementedError

    def test_admin_deletes_user(self, test_client, setup_uow):
        """Админ удаляет пользователя из системы"""
        raise NotImplementedError

    def test_admin_gets_all_users_list(self, test_client, setup_uow):
        """Админ получает список всех зарегистрированных пользователей"""
        raise NotImplementedError

    def test_admin_gets_specific_user_accounts(self, test_client, setup_uow):
        """Админ просматривает счета любого пользователя по его ID"""
        raise NotImplementedError

    def test_user_cannot_access_admin_endpoints(self, test_client, setup_uow):
        """Проверка прав доступа: обычный юзер получает 403 на админских роутах"""
        raise NotImplementedError
