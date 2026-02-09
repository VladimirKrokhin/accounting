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

import bcrypt
from adapters.repository import AbstractUserRepository
from dtos import (
    CreateOrUpdateUserDTO,
    AuthDTO,
    UserDTO,
    UserType,
)
from domain.models import UserId
from services.payment_system import UserDoesNotExists


def create_user(dto: CreateOrUpdateUserDTO):
    # TODO:
    raise NotImplementedError


def update_user(dto: UserDTO):
    # TODO:
    raise NotImplementedError


def delete_user(user_id: UserId):
    # TODO:

    raise NotImplementedError
