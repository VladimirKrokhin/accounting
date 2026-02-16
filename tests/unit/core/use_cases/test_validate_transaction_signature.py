from decimal import Decimal
from uuid import UUID
import pytest

from accounts.core.entities import TransactionId, AccountId, UserId, Money
from accounts.core.exceptions import SignatureIsNotValid
from accounts.core.use_cases.payment_system import validate_transaction_signature


def test_validate_transaction_signature_success() -> None:
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    transaction_id = UUID("5eae174f-7cd0-472c-bd36-35660f00132b")
    account_id = 1
    user_id = 1
    amount = Decimal(100)
    secret_key = "gfdmhghif38yrf9ew0jkf32"

    validate_transaction_signature(
        signature=signature,
        transaction_id=TransactionId(transaction_id),
        account_id=AccountId(account_id),
        user_id=UserId(user_id),
        amount=Money(amount),
        secret_key=secret_key,
    )


def test_validate_transaction_signature_wrong_transaction_key() -> None:
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    transaction_id = UUID("5eae174f-7cd0-472c-bd36-35660f00132a")
    account_id = 1
    user_id = 1
    amount = Decimal(100)
    secret_key = "gfdmhghif38yrf9ew0jkf32"

    with pytest.raises(SignatureIsNotValid):
        validate_transaction_signature(
            signature=signature,
            transaction_id=TransactionId(transaction_id),
            account_id=AccountId(account_id),
            user_id=UserId(user_id),
            amount=Money(amount),
            secret_key=secret_key,
        )


def test_validate_transaction_signature_wrong_account_key() -> None:
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    transaction_id = UUID("5eae174f-7cd0-472c-bd36-35660f00132b")
    account_id = 2
    user_id = 1
    amount = Decimal(100)
    secret_key = "gfdmhghif38yrf9ew0jkf32"

    with pytest.raises(SignatureIsNotValid):
        validate_transaction_signature(
            signature=signature,
            transaction_id=TransactionId(transaction_id),
            account_id=AccountId(account_id),
            user_id=UserId(user_id),
            amount=Money(amount),
            secret_key=secret_key,
        )


def test_validate_transaction_signature_wrong_user_id() -> None:
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    transaction_id = UUID("5eae174f-7cd0-472c-bd36-35660f00132b")
    account_id = 1
    user_id = 2
    amount = Decimal(100)
    secret_key = "gfdmhghif38yrf9ew0jkf32"

    with pytest.raises(SignatureIsNotValid):
        validate_transaction_signature(
            signature=signature,
            transaction_id=TransactionId(transaction_id),
            account_id=AccountId(account_id),
            user_id=UserId(user_id),
            amount=Money(amount),
            secret_key=secret_key,
        )


def test_validate_transaction_signature_wrong_amount() -> None:
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    transaction_id = UUID("5eae174f-7cd0-472c-bd36-35660f00132b")
    account_id = 1
    user_id = 1
    amount = Decimal(101)
    secret_key = "gfdmhghif38yrf9ew0jkf32"

    with pytest.raises(SignatureIsNotValid):
        validate_transaction_signature(
            signature=signature,
            transaction_id=TransactionId(transaction_id),
            account_id=AccountId(account_id),
            user_id=UserId(user_id),
            amount=Money(amount),
            secret_key=secret_key,
        )


def test_validate_transaction_signature_wrong_secret_key() -> None:
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    transaction_id = UUID("5eae174f-7cd0-472c-bd36-35660f00132b")
    account_id = 1
    user_id = 1
    amount = Decimal(100)
    secret_key = "gfdmhghif38yrf9ew0jkf33"

    with pytest.raises(SignatureIsNotValid):
        validate_transaction_signature(
            signature=signature,
            transaction_id=TransactionId(transaction_id),
            account_id=AccountId(account_id),
            user_id=UserId(user_id),
            amount=Money(amount),
            secret_key=secret_key,
        )
