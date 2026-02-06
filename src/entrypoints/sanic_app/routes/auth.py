from sanic import Blueprint

# Авторизация и получение информации о профиле пользователя

auth_bp = Blueprint("auth", url_prefix="/auth")


# Пользователь и администратор должен иметь следующие возможности:
# Авторизоваться по email/password
@auth_bp.post("/")
async def handle_auth(request):
    raise NotImplementedError


# Получить данные о себе(id, email, full_name)
@auth_bp.get("/me")
async def handle_me(request):
    raise NotImplementedError
