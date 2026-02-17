from sanic.app import Sanic
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, json


from accounts.core.use_cases.users import CreateUser, DeleteUser, UpdateUser
from accounts.dtos import (
    CreateOrUpdateUserDTO,
    CreateUserDTO,
    DeleteUserDTO,
    UpdateUserDTO,
    UserDTO,
)
from accounts.core.entities import Account, PaymentEntry
from accounts.core.exceptions import UserDoesNotExists, UserIsAlreadyExistsError
from accounts.core.types import UserId
from accounts.service_layer.unit_of_work import AbstractUnitOfWork
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
    app = request.app
    uow: AbstractUnitOfWork = app.ctx.uow
    current_user_id = request.ctx.user_id

    user_dto: UserDTO = await get_user_data_view(
        user_id=current_user_id,
        uow=uow,
    )

    json_body = {"user": dictify_user(user_dto)}
    return json(json_body, status=StatusCodes.SUCCESS)


# Пользователь должен иметь следующие возможности:
# Получить список своих счетов и балансов
@user_bp.get("/me/accounts")
async def get_current_user_accounts(request: Request) -> HTTPResponse:
    app = request.app
    uow: AbstractUnitOfWork = app.ctx.uow
    current_user_id = request.ctx.user_id

    try:
        user_accounts: list[Account] = await get_user_accounts_view(
            user_id=current_user_id,
            uow=uow,
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
    app = request.app
    uow: AbstractUnitOfWork = app.ctx.uow
    current_user_id = request.ctx.user_id

    try:
        user_payments: list[PaymentEntry] = await get_user_payments_view(
            user_id=current_user_id,
            uow=uow,
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
    app = request.app
    uow = app.ctx.uow
    create_user_data = request.json

    # FIXME: делай валидацию при помощи Pydantic
    create_user_dto = CreateOrUpdateUserDTO(
        email=create_user_data["email"],
        full_name=create_user_data["full_name"],
        password=create_user_data["password"],
    )

    create_user = CreateUserDTO(
        email=create_user_dto.email,
        full_name=create_user_dto.full_name,
        password=create_user_dto.password,
    )

    try:
        use_case = CreateUser(uow=uow)
        await use_case.execute(dto=create_user)
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
    app = request.app
    uow: AbstractUnitOfWork = app.ctx.uow

    delete_user = DeleteUserDTO(user_id=user_id)

    try:
        use_case = DeleteUser(uow)
        await use_case.execute(delete_user)
    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )

    return HTTPResponse(
        status=StatusCodes.SUCCESS_NO_CONTENT,
    )


@admin_bp.put("/<user_id:int>")
async def update_user(request: Request, user_id: int) -> HTTPResponse:
    app = request.app
    uow: AbstractUnitOfWork = app.ctx.uow

    update_info = request.json
    update_user_dto = CreateOrUpdateUserDTO(
        email=update_info["email"],
        full_name=update_info["full_name"],
        password=update_info["password"],
    )
    update_user = UpdateUserDTO(
        user_id=UserId(user_id),
        email=update_user_dto.email,
        full_name=update_user_dto.full_name,
        password=update_user_dto.password,
    )

    try:
        use_case = UpdateUser(uow=uow)
        await use_case.execute(dto=update_user)
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
    app = request.app
    uow = app.ctx.uow

    users = await get_users_view(uow=uow)

    json_body = {"users": [dictify_user(user) for user in users]}
    response = json(json_body, status=StatusCodes.SUCCESS)

    return response


# ... и список его счетов с балансами
@admin_bp.get("/<user_id:int>/accounts")
async def get_user_accounts(request: Request, user_id: int) -> HTTPResponse:
    app = request.app
    uow = app.ctx.uow

    user_accounts = await get_user_accounts_view(
        user_id=UserId(user_id),
        uow=uow,
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

user_bp.on_request(protected)
user_bp.on_request(is_user_or_admin)
admin_bp.on_request(protected)
admin_bp.on_request(is_admin)
