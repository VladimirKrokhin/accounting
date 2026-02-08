from sanic import Blueprint
from sanic.app import Sanic
from sanic.request import Request
from sanic.response import json, HTTPResponse

from entrypoints.sanic_app.status_codes import StatusCodes
from services.payment_system import (
    SignatureIsNotValid,
)
from domain.messages import HandlePaymentSystemTransaction
from domain.models import PaymentEntryIsNotUniqueError


# Обработка платежей
payment_bp = Blueprint("payments", url_prefix="/transactions")


# Веб-хуки
# Для работы с платежами: обработка вебхука от сторонней платежной системы.
@payment_bp.post("/")
async def handle_transaction(request: Request) -> HTTPResponse:
    app = Sanic.get_app("accounts")
    transaction_info = request.json
    transaction = HandlePaymentSystemTransaction(
        transaction_id=transaction_info["transaction_id"],
        user_id=transaction_info["user_id"],
        account_id=transaction_info["account_id"],
        amount=transaction_info["amount"],
        signature=transaction_info["signature"],
    )

    handler = app.ctx.handlers[HandlePaymentSystemTransaction]

    try:
        account_id, pe_id, is_new_account_created = handler(transaction)
    except SignatureIsNotValid:
        return json(
            {"status": "error", "message": "signature is not valid"},
            status=StatusCodes.ERROR_UNPROCESSABLE_ENTITY,
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
            "account_id": account_id,
            "payment_id": str(pe_id),
            "is_new_account_created": is_new_account_created,
        },
        status=StatusCodes.SUCCESS_CREATED,
    )
