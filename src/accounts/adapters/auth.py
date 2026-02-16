from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from accounts.config import AuthConfig
from accounts.core.types import UserId
from accounts.service_layer.unit_of_work import AbstractUnitOfWork

if TYPE_CHECKING:
    from accounts.dtos import UserDTO, UserType
    from accounts.adapters.repository import AbstractUserRepository

__all__ = [
    "authentificate_and_return_access_token",
    "extract_auth_payload_from_token",
]

# Исключения аутентификации и авторизации


class AuthError(Exception):
    pass


class AuthentificationError(AuthError):
    pass


class ExpiredSignatureError(AuthentificationError):
    pass


class InvalidTokenError(AuthentificationError):
    pass


class AuthorizationError(AuthError):
    pass


@dataclass(frozen=True)
class AuthDTO:
    email: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class AuthSuccessDTO:
    token: str = field(repr=False)


# Операции для аутентификации и авторизации пользователя
@dataclass(frozen=True)
class ExtractPayloadFromTokenDTO:
    token: str = field(repr=False)


@dataclass(frozen=True)
class AuthentificateDTO:
    email: str
    password: str = field(repr=False)


def is_user_type_in(
    user_id: UserId, user_types: list[UserType], user_repository: AbstractUserRepository
):
    """Тип пользователя находится в списке типов?"""
    user = user_repository.get_user(user_id)
    return user.user_type in user_types


def generate_password_hash(password: str):
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode(), salt)

    return hash.decode()


def check_password_by_hash(password: str, hashed_password: str) -> bool:
    """Проверить пароль по хешу."""
    password_byte = password.encode("utf-8")
    hashed_byte = hashed_password.encode("utf-8")

    res = bcrypt.checkpw(password_byte, hashed_byte)

    return res


def authentificate(dto: AuthDTO, uow: AbstractUnitOfWork) -> UserDTO:
    """Аутентифицировать пользователя."""

    with uow:
        user_repository = uow.users
        users = user_repository.get_users_by_email(dto.email)

        if len(users) != 1:
            raise AuthentificationError

        user = users[0]

        # Проверка хеша пароля
        is_password_valid = check_password_by_hash(
            password=dto.password, hashed_password=user.password_hash
        )

        if not is_password_valid:
            raise AuthentificationError

    return user


def generate_token(user: UserDTO, config: AuthConfig) -> str:
    """Сгенерировать токен для пользователя."""

    user_id = user.user_id
    if user_id is None:
        raise ValueError("user_id указан как None")

    payload = {
        "user_id": int(user_id),
        "exp": datetime.now(tz=timezone.utc) + config.expiration_time,
    }
    token = jwt.encode(
        payload, config.secret_key, algorithm=config.encryption_algorithm
    )

    return token


def authentificate_and_return_access_token(
    dto: AuthentificateDTO,
    config: AuthConfig,
    uow: AbstractUnitOfWork,
):
    auth_dto = AuthDTO(email=dto.email, password=dto.password)
    user_dto = authentificate(dto=auth_dto, uow=uow)
    token = generate_token(user=user_dto, config=config)

    ret = AuthSuccessDTO(
        token=token,
    )

    return ret


def extract_auth_payload_from_token(
    dto: ExtractPayloadFromTokenDTO,
    config: AuthConfig,
) -> UserId:

    try:
        payload = jwt.decode(
            dto.token,
            config.secret_key,
            algorithms=[config.encryption_algorithm],
        )
        user_id: UserId = payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise ExpiredSignatureError
    except jwt.InvalidTokenError:
        raise InvalidTokenError

    return user_id
