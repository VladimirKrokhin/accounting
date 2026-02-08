import jwt
from datetime import timedelta, datetime

from sanic.request import Request
from sanic.response import json
from adapters.repository import AbstractUserRepository
from dtos import AuthDTO, AuthSuccessDTO, UserDTO, UserDataDTO
from entrypoints.sanic_app.status_codes import StatusCodes
from services.user import AuthError, authentificate


# "Срок годности" токена
EXPIRATION_TIME = timedelta(hours=24)
# Алгоритм шифрования токена
ENCRYPTION_ALGORITHM = "HS256"
SECRET_KEY = "your-very-secret-key"


class AuthorizationError(AuthError):
    pass


def generate_token(user: UserDTO) -> str:
    """Сгенерировать токен для пользователя."""

    user_id = user.user_id
    if user_id is None:
        raise ValueError("user_id указан как None")

    payload = {"user_id": int(user_id), "exp": datetime.now() + EXPIRATION_TIME}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ENCRYPTION_ALGORITHM)

    return token


def authorize(dto: AuthDTO, user_repository: AbstractUserRepository):
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


async def protected(request: Request):
    token = request.headers.get("Authorization")

    if not token or not token.startswith("Bearer "):
        return json(
            {"status": "error", "message": "authorization required"},
            status=StatusCodes.ERROR_UNAUTHORIZED,
        )

    try:
        raw_token = token.split(" ")[1]
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ENCRYPTION_ALGORITHM])

        # Сохраняем данные в контекст
        request.ctx.user_id = payload.get("user_id")
        request.ctx.user_role = payload.get("role")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return json(
            {"status": "error", "message": "invalid or expired token"},
            status=StatusCodes.ERROR_UNAUTHORIZED,
        )
