from sanic import Blueprint


# Администратор
admin_bp = Blueprint("admin", url_prefix="/admin")


# Администратор должен иметь следующие возможности:
# Создать/Удалить/Обновить пользователя
@admin_bp.get("/users/<user_id:int>")
async def handle_user(request):
    raise NotImplementedError


# Получить список пользователей и список его счетов с балансами
@admin_bp.get("/users")
async def handle_users_with_accounts(request):
    raise NotImplementedError
