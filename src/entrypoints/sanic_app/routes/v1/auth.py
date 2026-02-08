from sanic.app import Sanic
from sanic import Blueprint, json
from sanic.request import Request

from entrypoints.sanic_app.routes.v1.user import dictify_user_data_dto
from entrypoints.sanic_app.status_codes import StatusCodes
from services.user import AuthError
from dtos import AuthDTO, AuthSuccessDTO
from entrypoints.sanic_app.auth_utils import authorize

auth_bp = Blueprint("auth", url_prefix="/auth")


def dictify_auth_success_dto(dto: AuthSuccessDTO):
    ret = {"access_token": dto.token, "user": dictify_user_data_dto(dto.data)}

    return ret


@auth_bp.post("/")
async def handle_auth(request: Request):
    app = Sanic.get_app("accounts")
    user_repo = app.ctx.user_repository

    try:
        data = AuthDTO(
            email=request.json.get("email"), password=request.json.get("password")
        )
    except AuthError:
        return json({"error": "auth error"}, status=StatusCodes.ERROR_UNAUTHORIZED)

    auth_success_dto = authorize(dto=data, user_repository=user_repo)
    json_body = dictify_auth_success_dto(dto=auth_success_dto)

    return json(body=json_body, status=StatusCodes.SUCCESS)
