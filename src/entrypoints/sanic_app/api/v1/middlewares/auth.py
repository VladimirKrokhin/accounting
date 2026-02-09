from sanic.app import Sanic
from sanic.request import Request
from sanic.response import json

from adapters.repository import AbstractUserRepository
from domain.models import UserId
from dtos import UserType
from entrypoints.sanic_app.status_codes import StatusCodes
from services.auth import (
    ExpiredSignatureError,
    InvalidTokenError,
    extract_auth_payload_from_token,
    is_user_type_in,
)


async def protected(request: Request):
    token = request.headers.get("Authorization")

    if not token or not token.startswith("Bearer "):
        return json(
            {"status": "error", "message": "authorization required"},
            status=StatusCodes.ERROR_UNAUTHORIZED,
        )

    try:
        raw_token = token.split(" ")[1]
        user_id = extract_auth_payload_from_token(raw_token)
        request.ctx.user_id = user_id
    except ExpiredSignatureError, InvalidTokenError:
        return json(
            {"status": "error", "message": "invalid or expired token"},
            status=StatusCodes.ERROR_UNAUTHORIZED,
        )


def get_user_type_required_middleware(allowed_user_types: list[UserType]):
    """Фабрика для миддлварей по типам пользователей."""

    async def middleware(request: Request):
        app = Sanic.get_app("accounts")
        user_repository: AbstractUserRepository = app.ctx.user_repository
        user_id: UserId = request.ctx.user_id

        if not user_id:
            return json(
                {"status": "error", "message": "Unauthorized"},
                status=StatusCodes.ERROR_UNAUTHORIZED,
            )

        is_user_type_in_allowed = is_user_type_in(
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
