# Пользователь должен иметь следующие возможности:
# 1. Авторизоваться по email/password
# 2. Получить данные о себе(id, email, full_name)
# 3. Получить список своих счетов и балансов
# 4. Получить список своих платежей

# Администратор должен иметь следующие возможности:
# 1. Авторизоваться по email/password
# 2. Получить данные о себе (id, email, full_name)
# 3. Создать/Удалить/Обновить пользователя
# 4. Получить список пользователей и список его счетов с балансами

from dtos import UserType, AuthDTO, UserDTO
from domain.models import UserId


def authorize(dto: AuthDTO) -> UserType:
    # TODO:
    raise NotImplementedError


def create_user(dto: CreateUserDto):
    # TODO:
    raise NotImplementedError


def update_user(dto: UserDTO):
    # TODO:
    raise NotImplementedError


def delete_user(user_id: UserId):
    # TODO:

    raise NotImplementedError
