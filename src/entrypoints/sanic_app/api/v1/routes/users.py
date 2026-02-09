from typing import Any

from sanic.app import Sanic
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, json


from adapters.repository import UserDoesNotExists
from domain.messages import CreateUser, DeleteUser, UpdateUser
from domain.models import Account, PaymentEntry, UserId
from dtos import CreateOrUpdateUserDTO, UserDTO, UserDataDTO
from entrypoints.sanic_app.api.v1.middlewares.auth import (
    is_admin,
    is_user_or_admin,
    protected,
)
from entrypoints.sanic_app.status_codes import StatusCodes
from services.user import UserIsAlreadyExistsError
from views import (
    get_user_accounts as get_user_accounts_view,
    get_user_payments as get_user_payments_view,
    get_user_data as get_user_data_view,
    get_users as get_users_view,
)


def dictify_payment(payment: PaymentEntry) -> dict[str, Any]:
    payment_id = payment.id_
    account_id = payment.account_id

    if payment_id is None or account_id is None:
        raise ValueError

    res = {
        "id": str(payment_id),
        "transaction_id": str(payment.transaction_id),
        "account_id": int(account_id),
        "amount": payment.amount,
        "is_accrued": payment.is_accrued,
    }

    return res


def dictify_account(account: Account) -> dict[str, Any]:
    account_id = account.id_

    if account_id is None:
        raise ValueError

    res = {
        "id": int(account_id),
        "user_id": int(account.user_id),
        "balance": account.balance,
    }

    return res


def dictify_user_data_dto(dto: UserDataDTO):
    ret = {
        "id": dto.user_id,
        "email": dto.email,
        "full_name": dto.full_name,
        "user_type": str(dto.user_type),
    }

    return ret


# Пользователь

user_bp = Blueprint("user")
admin_bp = Blueprint("admin")


# Пользователь и администратор должен иметь следующие возможности:
# Получить данные о себе(id, email, full_name)
@user_bp.get("/me")
async def handle_me(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    user_repository = app.ctx.user_repository
    current_user_id = request.ctx.user_id

    user_dto = get_user_data_view(
        user_id=current_user_id, user_repository=user_repository
    )

    user_data_dto = UserDataDTO(
        user_id=user_dto.user_id,
        email=user_dto.email,
        full_name=user_dto.full_name,
        user_type=user_dto.user_type,
    )

    json_body = dictify_user_data_dto(user_data_dto)
    return json(json_body, status=StatusCodes.SUCCESS)


# Пользователь должен иметь следующие возможности:
# Получить список своих счетов и балансов
@user_bp.get("/me/accounts")
async def get_current_user_accounts(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    user_repository = app.ctx.user_repository
    account_repository = app.ctx.account_repository
    current_user_id = request.ctx.user_id

    try:
        user_accounts = get_user_accounts_view(
            user_id=current_user_id,
            account_repository=account_repository,
            user_repository=user_repository,
        )
    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )

    json_body = [dictify_account(account) for account in user_accounts]
    return json(json_body, status=StatusCodes.SUCCESS)


# Получить список своих платежей
@user_bp.get("/me/payments")
async def get_current_user_payments(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    user_repository = app.ctx.user_repository
    account_repository = app.ctx.account_repository
    current_user_id = request.ctx.user_id

    try:
        user_payments = get_user_payments_view(
            user_id=current_user_id,
            account_repository=account_repository,
            user_repository=user_repository,
        )
    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )

    json_body = [dictify_payment(payment) for payment in user_payments]
    return json(json_body, status=StatusCodes.SUCCESS)


# Администратор должен иметь следующие возможности:
# Создать/Удалить/Обновить пользователя
@admin_bp.post("/")
async def create_user(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    create_user_data = request.json

    # FIXME: делай валидацию при помощи Pydantic
    create_user_dto = CreateOrUpdateUserDTO(
        email=create_user_data["email"],
        full_name=create_user_data["full_name"],
        password=create_user_data["password"],
    )

    create_user = CreateUser(
        email=create_user_dto.email,
        full_name=create_user_dto.full_name,
        password=create_user_dto.password,
    )

    handler = app.ctx.handlers[CreateUser]

    try:
        user_id = handler(create_user)
    except UserIsAlreadyExistsError:
        return json(
            {"status": "error", "message": "user with email is already exists"},
            status=StatusCodes.ERROR_CONFLICT,
        )

    return json(
        {
            "status": "success",
            "message": "user created",
            "user_id": user_id,
        },
        status=StatusCodes.SUCCESS_CREATED,
    )


@admin_bp.delete("/<user_id:int>")
async def delete_user(request: Request, user_id: int) -> HTTPResponse:
    app = Sanic.get_app("accounts")

    delete_user = DeleteUser(user_id=user_id)
    handler = app.ctx.handlers[DeleteUser]

    try:
        handler(delete_user)
    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )

    return json(
        {
            "status": "success",
            "message": "user deleted",
            "user_id": user_id,
        },
        status=StatusCodes.SUCCESS_NO_CONTENT,
    )


@admin_bp.post("/<user_id:int>")
async def update_user(request: Request, user_id: int) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    update_info = request.json
    update_user_dto = CreateOrUpdateUserDTO(
        email=update_info["email"],
        full_name=update_info["full_name"],
        password=update_info["password"],
    )
    update_user = UpdateUser(
        user_id=user_id,
        email=update_user_dto.email,
        full_name=update_user_dto.full_name,
        password=update_user_dto.password,
    )

    handler = app.ctx.handlers[UpdateUser]

    try:
        user_id = handler(update_user)
    except UserIsAlreadyExistsError:
        return json(
            {"status": "error", "message": "user with email is already exists"},
            status=StatusCodes.ERROR_CONFLICT,
        )

    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )

    return json(
        {
            "status": "success",
            "message": "user updated",
            "user_id": user_id,
        },
        status=StatusCodes.SUCCESS_NO_CONTENT,
    )


# Получить список пользователей...
def dictify_user(user: UserDTO) -> dict[str, Any]:
    res = {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "user_type": str(user.user_type),
    }

    return res


@admin_bp.get("/")
async def get_users(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    user_repository = app.ctx.user_repository

    users = get_users_view(user_repository=user_repository)

    json_body = [dictify_user(user) for user in users]
    response = json(json_body, status=StatusCodes.SUCCESS)

    return response


# ... и список его счетов с балансами
@admin_bp.get("/<user_id:int>/accounts")
async def get_user_accounts(request: Request, user_id: int) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    account_repository = app.ctx.account_repository
    user_repository = app.ctx.user_repository

    user_accounts = get_user_accounts_view(
        user_id=UserId(user_id),
        account_repository=account_repository,
        user_repository=user_repository,
    )
    json_body = [dictify_account(account) for account in user_accounts]
    response = json(body=json_body, status=StatusCodes.SUCCESS)

    return response


users_api = Blueprint.group(user_bp, admin_bp, url_prefix="/users")
user_bp.middleware(protected, attach_to="request")
user_bp.middleware(is_user_or_admin, attach_to="request")
admin_bp.middleware(protected, attach_to="request")
admin_bp.middleware(is_admin, attach_to="request")
