from sanic.app import Sanic
from sanic import Blueprint, json
from sanic.request import Request

from accounts.adapters.auth import (
    AuthError,
    authentificate_and_return_access_token,
    AuthSuccessDTO,
    AuthentificateDTO,
)
from accounts.config import AuthConfig
from accounts.entrypoints.sanic_app.api.v1.marshallers import dictify_auth_success_dto
from accounts.entrypoints.sanic_app.status_codes import StatusCodes
from accounts.service_layer.unit_of_work import AbstractUnitOfWork

__all__ = ["auth_bp"]

auth_bp = Blueprint("auth", url_prefix="/auth")


@auth_bp.post("/")
async def handle_auth(request: Request):
    app = request.app
    uow: AbstractUnitOfWork = app.ctx.uow

    try:
        dto = AuthentificateDTO(
            email=request.json.get("email"),
            password=request.json.get("password"),
        )
        config = AuthConfig(
            secret_key=app.config.AUTH_SECRET_KEY,
            expiration_time=app.config.AUTH_EXPIRATION_TIME,
            encryption_algorithm=app.config.AUTH_ENCRYPTION_ALGORITHM,
        )
        auth_success_dto: AuthSuccessDTO = await authentificate_and_return_access_token(
            dto=dto, config=config, uow=uow
        )
    except AuthError:
        return json({"error": "auth error"}, status=StatusCodes.ERROR_UNAUTHORIZED)

    json_body = dictify_auth_success_dto(dto=auth_success_dto)

    return json(body=json_body, status=StatusCodes.SUCCESS)
