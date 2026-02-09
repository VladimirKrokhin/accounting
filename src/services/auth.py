import bcrypt
import jwt
from datetime import timedelta, datetime

from adapters.repository import AbstractUserRepository, UserDoesNotExists
from domain.models import UserId
from dtos import AuthDTO, AuthSuccessDTO, UserDTO, UserDataDTO, UserType

# "Срок годности" токена
EXPIRATION_TIME = timedelta(hours=24)
# Алгоритм шифрования токена
ENCRYPTION_ALGORITHM = "HS256"
SECRET_KEY = "your-very-secret-key"


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


def authentificate(dto: AuthDTO, user_repository: AbstractUserRepository) -> UserDTO:
    """Аутентифицировать пользователя."""
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


def generate_token(user: UserDTO) -> str:
    """Сгенерировать токен для пользователя."""

    user_id = user.user_id
    if user_id is None:
        raise ValueError("user_id указан как None")

    payload = {"user_id": int(user_id), "exp": datetime.now() + EXPIRATION_TIME}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ENCRYPTION_ALGORITHM)

    return token


def authentificate_and_return_access_token(
    dto: AuthDTO, user_repository: AbstractUserRepository
):
    user_dto = authentificate(dto=dto, user_repository=user_repository)
    token = generate_token(user_dto)

    ret = AuthSuccessDTO(
        token=token,
        data=UserDataDTO(
            user_id=user_dto.user_id,
            email=user_dto.email,
            full_name=user_dto.full_name,
            user_type=user_dto.user_type,
        ),
    )

    return ret


def extract_auth_payload_from_token(token: str) -> UserId:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ENCRYPTION_ALGORITHM])
        user_id: UserId = payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise ExpiredSignatureError
    except jwt.InvalidTokenError:
        raise InvalidTokenError

    return user_id
