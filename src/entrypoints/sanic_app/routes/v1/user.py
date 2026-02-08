from sanic import Blueprint
from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json
from typing import Any


from domain.models import Account, PaymentEntry, UserId
from dtos import UserDTO
from entrypoints.sanic_app.status_codes import StatusCodes
from views import (
    get_user_accounts as get_user_accounts_view,
    get_user_payments as get_user_payments_view,
    get_user_data as get_user_data_view,
    get_users as get_users_view,
)

# Пользователь

user_bp = Blueprint("user", url_prefix="/users")


# Пользователь и администратор должен иметь следующие возможности:
# Получить данные о себе(id, email, full_name)
@user_bp.get("/me")
async def handle_me(request: Request) -> HTTPResponse:
    raise NotImplementedError


# Пользователь должен иметь следующие возможности:
# Получить список своих счетов и балансов
@user_bp.get("/me/accounts")
async def get_current_user_accounts(request: Request) -> HTTPResponse:
    raise NotImplementedError


# Получить список своих платежей
@user_bp.get("/me/payments")
async def get_current_user_payments(request: Request) -> HTTPResponse:
    raise NotImplementedError


# Администратор должен иметь следующие возможности:
# Создать/Удалить/Обновить пользователя
@user_bp.post("/")
async def create_user(request: Request) -> HTTPResponse:
    raise NotImplementedError


@user_bp.delete("/<user_id:int>")
async def delete_user(request: Request, user_id: int) -> HTTPResponse:
    raise NotImplementedError


@user_bp.patch("/<user_id:int>")
async def update_user(request: Request, user_id: int) -> HTTPResponse:
    raise NotImplementedError


# Получить список пользователей...
def dictify_user(user: UserDTO) -> dict[str, Any]:
    res = {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "user_type": str(user.user_type),
    }

    return res


@user_bp.get("/")
async def get_users(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    user_repository = app.ctx.user_repository

    users = get_users_view(user_repository=user_repository)

    json_body = [dictify_user(user) for user in users]
    response = json(json_body, status=StatusCodes.SUCCESS)

    return response


def dictify_payment(payment: PaymentEntry) -> dict[str, Any]:
    res = {
        "id": str(payment.id_),
        "transaction_id": str(payment.transaction_id),
        "account_id": int(payment.account_id),
        "amount": payment.amount,
        "is_accrued": payment.is_accrued,
    }

    return res


def dictify_account(account: Account) -> dict[str, Any]:
    res = {
        "id": int(account.id_),
        "user_id": int(account.user_id),
        "balance": account.balance,
        "payments": [dictify_payment(payment) for payment in account.payments],
    }

    return res


# ... и список его счетов с балансами
@user_bp.get("/<user_id:int>/accounts")
async def get_user_accounts(request: Request, user_id: int) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    account_repository = app.ctx.account_repository

    user_accounts = get_user_accounts_view(
        user_id=UserId(user_id), account_repository=account_repository
    )
    json_body = [dictify_account(account) for account in user_accounts]
    response = json(body=json_body, status=StatusCodes.SUCCESS)

    return response
