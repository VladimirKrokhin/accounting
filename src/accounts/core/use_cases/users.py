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
    CreateUserDTO,
    DeleteUserDTO,
    UpdateUserDTO,
)

from accounts.core.types import UserId
from accounts.core.exceptions import UserIsAlreadyExistsError, UserDoesNotExists

from accounts.adapters.auth import generate_password_hash
from accounts.service_layer.unit_of_work import AbstractUnitOfWork


class CreateUser:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: CreateUserDTO) -> int:
        with self.uow as uow:
            user_repository = uow.users
            is_user_exists = await user_repository.does_user_exist_by_email(dto.email)

            if is_user_exists:
                raise UserIsAlreadyExistsError(
                    "Пользователь с указанным email уже существует"
                )

            password_hash = generate_password_hash(dto.password)

            user = UserDTO(
                email=dto.email,
                full_name=dto.full_name,
                password_hash=password_hash,
                user_type=UserType.USER,
            )
            user_id = await user_repository.save_user(user)

            uow.commit()

        return user_id


class UpdateUser:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: UpdateUserDTO) -> UserId:
        with self.uow as uow:
            user_repository = uow.users
            is_user_exists = await user_repository.does_user_exist(dto.user_id)

            if not is_user_exists:
                raise UserDoesNotExists(
                    "Пользователь с указанным user_id не существует"
                )

            users_with_exact_email = await user_repository.get_users_by_email(dto.email)
            for user in users_with_exact_email:
                if user.user_id != dto.user_id:
                    raise UserIsAlreadyExistsError(
                        "Существует другой пользователь с указанным email"
                    )

            password_hash = generate_password_hash(dto.password)

            user = UserDTO(
                user_id=dto.user_id,
                email=dto.email,
                full_name=dto.full_name,
                password_hash=password_hash,
                user_type=UserType.USER,
            )
            user_id = await user_repository.save_user(user)

            uow.commit()

        return user_id


class DeleteUser:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: DeleteUserDTO) -> None:
        user_id = dto.user_id
        with self.uow as uow:
            user_repository = uow.users
            is_user_exists = await user_repository.does_user_exist(user_id)

            if not is_user_exists:
                raise UserDoesNotExists(
                    "Пользователь с указанным user_id не существует"
                )

            await user_repository.delete_user(user_id)

            uow.commit()
