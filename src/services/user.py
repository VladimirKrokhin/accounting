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

from dataclasses import dataclass
from enum import StrEnum

from domain import UserId


class UserType(StrEnum):
    ADMIN = "admin"
    USER = "user"


@dataclass(frozen=True)
class AuthDTO:
    email: str
    password: str


@dataclass(frozen=True)
class UserDTO:
    user_id: UserId
    email: str
    full_name: str
    user_type: UserType


@dataclass(frozen=True)
class AuthSuccessDTO:
    token: str
    data: UserDTO


def authorize(dto: AuthDTO) -> UserType:
    # TODO:
    raise NotImplementedError


def get_user_data(user_id: UserId) -> UserDTO:
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
