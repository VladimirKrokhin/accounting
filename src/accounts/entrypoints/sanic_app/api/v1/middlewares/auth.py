from sanic.app import Sanic
from sanic.request import Request
from sanic.response import json

from accounts.config import AuthConfig
from accounts.dtos import UserType
from accounts.core.types import UserId
from accounts.adapters.repository import AbstractUserRepository
from accounts.adapters.auth import (
    ExpiredSignatureError,
    ExtractPayloadFromTokenDTO,
    InvalidTokenError,
    is_user_type_in,
    extract_auth_payload_from_token,
)
from accounts.entrypoints.sanic_app.status_codes import StatusCodes
from accounts.service_layer.unit_of_work import AbstractUnitOfWork

__all__ = ["protected", "is_user", "is_admin", "is_user_or_admin"]


async def protected(request: Request):
    token = request.headers.get("Authorization")

    if not token or not token.startswith("Bearer "):
        return json(
            {"status": "error", "message": "authorization required"},
            status=StatusCodes.ERROR_UNAUTHORIZED,
        )

    app = request.app

    try:
        raw_token = token.split(" ")[1]
        dto = ExtractPayloadFromTokenDTO(
            token=raw_token,
        )
        config = AuthConfig(
            expiration_time=app.config.AUTH_EXPIRATION_TIME,
            encryption_algorithm=app.config.AUTH_ENCRYPTION_ALGORITHM,
            secret_key=app.config.AUTH_SECRET_KEY,
        )
        user_id = extract_auth_payload_from_token(dto=dto, config=config)
        request.ctx.user_id = user_id
    except ExpiredSignatureError, InvalidTokenError:
        return json(
            {"status": "error", "message": "invalid or expired token"},
            status=StatusCodes.ERROR_UNAUTHORIZED,
        )


async def get_user_type_required_middleware(allowed_user_types: list[UserType]):
    """Фабрика для миддлварей по типам пользователей."""

    async def middleware(request: Request):
        app = request.app
        uow: AbstractUnitOfWork = app.ctx.uow
        user_repository: AbstractUserRepository = uow.users
        user_id: UserId = request.ctx.user_id

        if not user_id:
            return json(
                {"status": "error", "message": "Unauthorized"},
                status=StatusCodes.ERROR_UNAUTHORIZED,
            )

        is_user_type_in_allowed = await is_user_type_in(
            user_id=user_id,
            user_types=allowed_user_types,
            user_repository=user_repository,
        )

        if not is_user_type_in_allowed:
            return json(
                {"status": "error", "message": "Access denied"},
                status=StatusCodes.ERROR_FORBIDDEN,
            )

    return middleware


is_user = get_user_type_required_middleware(allowed_user_types=[UserType.USER])
is_admin = get_user_type_required_middleware(allowed_user_types=[UserType.ADMIN])
is_user_or_admin = get_user_type_required_middleware(
    allowed_user_types=[UserType.USER, UserType.ADMIN]
)
