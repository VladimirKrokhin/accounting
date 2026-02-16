from typing import Any

from accounts.adapters.auth import AuthSuccessDTO
from accounts.core.entities import Account, PaymentEntry
from accounts.dtos import UserDTO


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

    return {"payments": res}


def dictify_account(account: Account) -> dict[str, Any]:
    account_id = account.id_

    if account_id is None:
        raise ValueError

    res = {
        "id": int(account_id),
        "user_id": int(account.user_id),
        "balance": account.balance,
    }

    return {"account": res}


def dictify_user(user: UserDTO) -> dict[str, Any]:
    res = {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "user_type": str(user.user_type),
    }

    return res


def dictify_auth_success_dto(dto: AuthSuccessDTO):
    ret = {"access_token": dto.token}

    return ret
