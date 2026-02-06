import pytest

from domain import Account, AccountId, Money, TransactionId, UserId
from adapters.repository import FakeAccountRepository
from services.payment_system import (
    HandlePaymentSystemTransactionDto,
    process_payment_system_transaction,
)


def test_process_payment_system_transaction_success_user_has_account():
    secret = "gfdmhghif38yrf9ew0jkf32"
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"

    transaction_id = TransactionId("5eae174f-7cd0-472c-bd36-35660f00132b")
    user_id = UserId(1)
    account_id = AccountId(1)
    amount = Money(100)
    start_balance = Money(0)

    repository = FakeAccountRepository()

    account = Account(
        id_=account_id,
        user_id=user_id,
        balance=start_balance,
    )
    repository.save_account(account)

    dto = HandlePaymentSystemTransactionDto(
        transaction_id=transaction_id,
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        signature=signature,
    )

    process_payment_system_transaction(
        repository=repository,
        transaction=dto,
        secret=secret,
    )

    account = repository.get_account_by_id(account_id)

    # Платеж появился на счете
    assert len(account.payments) == 1
    # Счет пополнился на сумму платежа
    assert account.balance == start_balance + amount

    p = tuple(account.payments)[0]
    # Платеж имеет необходимый transaction_id
    assert p.transaction_id == transaction_id
    # Платеж указан начисленным
    assert p.is_accrued == True


def test_process_payment_system_transaction_success_user_has_not_account():
    secret = "gfdmhghif38yrf9ew0jkf32"
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"

    transaction_id = TransactionId("5eae174f-7cd0-472c-bd36-35660f00132b")
    user_id = UserId(1)
    amount = Money(100)
    account_id = AccountId(1)

    repository = FakeAccountRepository()

    dto = HandlePaymentSystemTransactionDto(
        transaction_id=transaction_id,
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        signature=signature,
    )

    # Счета нет
    assert not repository.is_user_has_account(user_id=user_id, account_id=account_id)

    pe_id = process_payment_system_transaction(
        repository=repository,
        transaction=dto,
        secret=secret,
    )

    account = repository.get_account_by_id(account_id)

    # Платеж появился на счете
    assert len(account.payments) == 1
    # Счет имеет значение суммы платежа
    assert account.balance == amount

    p = tuple(account.payments)[0]
    # Платеж имеет необходимый transaction_id
    assert p.transaction_id == transaction_id
    # Платеж указан начисленным
    assert p.is_accrued == True
