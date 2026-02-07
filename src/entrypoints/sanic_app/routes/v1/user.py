from sanic import Blueprint

# Пользователь

user_bp = Blueprint("user", url_prefix="/users")


# Пользователь должен иметь следующие возможности:
# Получить список своих счетов и балансов
@user_bp.get("/<user_id:int>/accounts")
async def handle_user_accounts(request):
    raise NotImplementedError


# Получить список своих платежей
@user_bp.get("/<user_id:int>/payments")
async def handle_user_payments(request):
    raise NotImplementedError
