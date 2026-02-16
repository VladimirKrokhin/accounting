from sanic import Blueprint
from sanic.app import Sanic
from sanic.request import Request
from sanic.response import json, HTTPResponse


from accounts.domain.messages import HandlePaymentSystemTransaction
from accounts.domain.exceptions import (
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
    app = Sanic.get_app("accounts")
    mb = app.ctx.message_bus

    transaction_info = request.json
    transaction = HandlePaymentSystemTransaction(
        transaction_id=transaction_info["transaction_id"],
        user_id=transaction_info["user_id"],
        account_id=transaction_info["account_id"],
        amount=transaction_info["amount"],
        signature=transaction_info["signature"],
        secret_key=app.config.PAYMENT_SYSTEM_SECRET_KEY,
    )

    try:
        mb.handle(transaction)
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
