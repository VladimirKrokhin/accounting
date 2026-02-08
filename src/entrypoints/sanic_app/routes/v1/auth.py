from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse

# Авторизация и получение информации о профиле пользователя

auth_bp = Blueprint("auth", url_prefix="/auth")


# Пользователь и администратор должен иметь следующие возможности:
# Авторизоваться по email/password
@auth_bp.post("/")
async def handle_auth(request: Request) -> HTTPResponse:
    raise NotImplementedError
