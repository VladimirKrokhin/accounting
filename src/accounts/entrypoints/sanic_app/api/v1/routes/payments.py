from sanic import Blueprint
from sanic.app import Sanic
from sanic.request import Request
from sanic.response import json, HTTPResponse


from accounts.dtos import HandlePaymentSystemTransactionDTO
from accounts.config import PaymentSystemConfig
from accounts.core.use_cases.payment_system import ProcessPaymentSystemWebHook
from accounts.core.exceptions import (
    PaymentEntryIsNotUniqueError,
    SignatureIsNotValid,
    UserDoesNotExists,
)
from accounts.entrypoints.sanic_app.status_codes import StatusCodes

__all__ = ["payment_bp"]

# Обработка платежей
payment_bp = Blueprint("payments", url_prefix="/transactions")


# Веб-хуки
# Для работы с платежами: обработка вебхука от сторонней платежной системы.
@payment_bp.post("/")
async def handle_transaction(request: Request) -> HTTPResponse:
    app = request.app
    uow = app.ctx.uow

    transaction_info = request.json
    transaction_dto = HandlePaymentSystemTransactionDTO(
        transaction_id=transaction_info["transaction_id"],
        user_id=transaction_info["user_id"],
        account_id=transaction_info["account_id"],
        amount=transaction_info["amount"],
        signature=transaction_info["signature"],
    )
    config = PaymentSystemConfig(
        secret_key=app.config.PAYMENT_SYSTEM_SECRET_KEY,
    )

    try:
        use_case = ProcessPaymentSystemWebHook(uow=uow, config=config)
        await use_case.execute(transaction_dto)
    except SignatureIsNotValid:
        return json(
            {"status": "error", "message": "signature is not valid"},
            status=StatusCodes.ERROR_UNPROCESSABLE_ENTITY,
        )
    except UserDoesNotExists:
        return json(
            {"status": "error", "message": "user does not exists"},
            status=StatusCodes.ERROR_NOT_FOUND,
        )
    except PaymentEntryIsNotUniqueError:
        return json(
            {"status": "error", "message": "transaction already exists"},
            status=StatusCodes.ERROR_CONFLICT,
        )

    return json(
        {
            "status": "success",
            "message": "transaction processed",
        },
        status=StatusCodes.SUCCESS_CREATED,
    )
