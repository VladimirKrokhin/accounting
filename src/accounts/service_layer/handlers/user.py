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

from accounts.dtos import (
    UserDTO,
    UserType,
)

from accounts.domain.types import UserId
from accounts.domain.messages import CreateUser, DeleteUser, UpdateUser
from accounts.domain.exceptions import UserIsAlreadyExistsError, UserDoesNotExists
from accounts.adapters.auth import generate_password_hash
from accounts.service_layer.unit_of_work import AbstractUnitOfWork

__all__ = ["create_user", "update_user", "delete_user"]


def create_user(message: CreateUser, uow: AbstractUnitOfWork) -> UserId:
    user_repository = uow.users
    is_user_exists = user_repository.is_user_exists_by_email(message.email)

    if is_user_exists:
        raise UserIsAlreadyExistsError("Пользователь с указанным email уже существует")

    password_hash = generate_password_hash(message.password)

    user = UserDTO(
        email=message.email,
        full_name=message.full_name,
        password_hash=password_hash,
        user_type=UserType.USER,
    )
    user_id = user_repository.save_user(user)

    return user_id


def update_user(message: UpdateUser, uow: AbstractUnitOfWork) -> UserId:
    user_repository = uow.users
    is_user_exists = user_repository.is_user_exists(message.user_id)

    if not is_user_exists:
        raise UserDoesNotExists("Пользователь с указанным user_id не существует")

    users_with_exact_email = user_repository.get_users_by_email(message.email)
    for user in users_with_exact_email:
        if user.user_id != message.user_id:
            raise UserIsAlreadyExistsError(
                "Существует другой пользователь с указанным email"
            )

    password_hash = generate_password_hash(message.password)

    user = UserDTO(
        user_id=message.user_id,
        email=message.email,
        full_name=message.full_name,
        password_hash=password_hash,
        user_type=UserType.USER,
    )
    user_id = user_repository.save_user(user)

    return user_id


def delete_user(message: DeleteUser, uow: AbstractUnitOfWork) -> None:
    user_repository = uow.users
    user_id = message.user_id
    is_user_exists = user_repository.is_user_exists(user_id)

    if not is_user_exists:
        raise UserDoesNotExists("Пользователь с указанным user_id не существует")

    user_repository.delete_user(user_id)
