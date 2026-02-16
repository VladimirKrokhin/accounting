from sanic.app import Sanic
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, json


from accounts.dtos import CreateOrUpdateUserDTO, UserDTO
from accounts.domain.models import Account, PaymentEntry
from accounts.domain.exceptions import UserDoesNotExists, UserIsAlreadyExistsError
from accounts.domain.types import UserId
from accounts.domain.messages import CreateUser, DeleteUser, UpdateUser
from accounts.service_layer.message_bus import MessageBus
from accounts.views import (
    get_user_accounts as get_user_accounts_view,
    get_user_payments as get_user_payments_view,
    get_user_data as get_user_data_view,
    get_users as get_users_view,
)
from accounts.entrypoints.sanic_app.api.v1.marshallers import (
    dictify_account,
    dictify_payment,
    dictify_user,
)
from accounts.entrypoints.sanic_app.api.v1.middlewares.auth import (
    is_admin,
    is_user_or_admin,
    protected,
)
from accounts.entrypoints.sanic_app.status_codes import StatusCodes

__all__ = ["user_bp", "admin_bp"]

# Пользователь

user_bp = Blueprint("user")
admin_bp = Blueprint("admin")


# Пользователь и администратор должен иметь следующие возможности:
# Получить данные о себе(id, email, full_name)
@user_bp.get("/me")
async def handle_me(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    mb: MessageBus = app.ctx.message_bus
    current_user_id = request.ctx.user_id

    user_dto: UserDTO = get_user_data_view(
        user_id=current_user_id, user_repository=mb.uow.users
    )

    json_body = {"user": dictify_user(user_dto)}
    return json(json_body, status=StatusCodes.SUCCESS)


# Пользователь должен иметь следующие возможности:
# Получить список своих счетов и балансов
@user_bp.get("/me/accounts")
async def get_current_user_accounts(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    mb: MessageBus = app.ctx.message_bus
    current_user_id = request.ctx.user_id

    try:
        user_accounts: list[Account] = get_user_accounts_view(
            user_id=current_user_id,
            account_repository=mb.uow.accounts,
            user_repository=mb.uow.users,
        )
    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )

    json_body = {
        "user": {
            "id": current_user_id,
            "accounts": [dictify_account(account) for account in user_accounts],
        }
    }

    return json(json_body, status=StatusCodes.SUCCESS)


# Получить список своих платежей
@user_bp.get("/me/payments")
async def get_current_user_payments(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    mb: MessageBus = app.ctx.message_bus
    current_user_id = request.ctx.user_id

    try:
        user_payments: list[PaymentEntry] = get_user_payments_view(
            user_id=current_user_id,
            account_repository=mb.uow.accounts,
            user_repository=mb.uow.users,
        )
    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )

    json_body = {
        "user": {
            "id": current_user_id,
            "payments": [dictify_payment(payment) for payment in user_payments],
        }
    }
    return json(json_body, status=StatusCodes.SUCCESS)


# Администратор должен иметь следующие возможности:
# Создать/Удалить/Обновить пользователя
@admin_bp.post("/")
async def create_user(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    mb: MessageBus = app.ctx.message_bus
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

    try:
        mb.handle(create_user)
    except UserIsAlreadyExistsError:
        return json(
            {"status": "error", "message": "user with email is already exists"},
            status=StatusCodes.ERROR_CONFLICT,
        )

    return json(
        {
            "status": "success",
            "message": "user created",
        },
        status=StatusCodes.SUCCESS_CREATED,
    )


@admin_bp.delete("/<user_id:int>")
async def delete_user(request: Request, user_id: int) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    mb: MessageBus = app.ctx.message_bus

    delete_user = DeleteUser(user_id=user_id)

    try:
        mb.handle(delete_user)
    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )

    return HTTPResponse(
        status=StatusCodes.SUCCESS_NO_CONTENT,
    )


@admin_bp.post("/<user_id:int>")
async def update_user(request: Request, user_id: int) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    mb: MessageBus = app.ctx.message_bus

    update_info = request.json
    update_user_dto = CreateOrUpdateUserDTO(
        email=update_info["email"],
        full_name=update_info["full_name"],
        password=update_info["password"],
    )
    update_user = UpdateUser(
        user_id=UserId(user_id),
        email=update_user_dto.email,
        full_name=update_user_dto.full_name,
        password=update_user_dto.password,
    )

    try:
        mb.handle(update_user)
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

    return HTTPResponse(
        status=StatusCodes.SUCCESS_NO_CONTENT,
    )


# Получить список пользователей...


@admin_bp.get("/")
async def get_users(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    mb: MessageBus = app.ctx.message_bus

    users = get_users_view(user_repository=mb.uow.users)

    json_body = {"users": [dictify_user(user) for user in users]}
    response = json(json_body, status=StatusCodes.SUCCESS)

    return response


# ... и список его счетов с балансами
@admin_bp.get("/<user_id:int>/accounts")
async def get_user_accounts(request: Request, user_id: int) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    mb: MessageBus = app.ctx.message_bus

    user_accounts = get_user_accounts_view(
        user_id=UserId(user_id),
        account_repository=mb.uow.accounts,
        user_repository=mb.uow.users,
    )
    json_body = {
        "user": {
            "id": user_id,
            "accounts": [dictify_account(account) for account in user_accounts],
        }
    }
    response = json(body=json_body, status=StatusCodes.SUCCESS)

    return response


users_api = Blueprint.group(user_bp, admin_bp, url_prefix="/users")
user_bp.middleware(protected, attach_to="request")
user_bp.middleware(is_user_or_admin, attach_to="request")
admin_bp.middleware(protected, attach_to="request")
admin_bp.middleware(is_admin, attach_to="request")
