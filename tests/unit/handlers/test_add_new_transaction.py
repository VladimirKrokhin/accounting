from decimal import Decimal
from uuid import uuid4
import pytest

from accounts.domain.exceptions import PaymentEntryIsNotUniqueError
from accounts.domain.models import (
    TransactionId,
    Account,
    Money,
    UserId,
    AccountId,
)
from accounts.adapters.repository import FakeAccountRepository
from accounts.service_layer.handlers.payment_system import add_new_transaction


def test_add_new_transaction_success():
    account_repository = FakeAccountRepository()
    account = Account(id_=AccountId(1), user_id=UserId(1), balance=Money(Decimal(1)))
    tr_id = TransactionId(uuid4())

    add_new_transaction(
        account_repository=account_repository,
        account=account,
        transaction_id=tr_id,
        amount=Money(Decimal(100)),
    )

    # Платеж добавлен
    assert len(account.payments) == 1
    p = tuple(account.payments)[0]
    assert p.transaction_id == tr_id
    assert p.account_id == account.id_

    # Баланс не изменен
    assert account.balance == Money(Decimal(1))

    # Платеж не начислен
    assert p.is_accrued == False


def test_add_new_transaction_duplicate():
    account_repository = FakeAccountRepository()
    account1 = Account(id_=AccountId(1), user_id=UserId(1), balance=Money(Decimal(1)))
    account2 = Account(id_=AccountId(2), user_id=UserId(1), balance=Money(Decimal(1)))
    tr_id = TransactionId(uuid4())

    add_new_transaction(
        account_repository=account_repository,
        account=account1,
        transaction_id=tr_id,
        amount=Money(Decimal(100)),
    )

    with pytest.raises(PaymentEntryIsNotUniqueError, match="Транзакция дублируется"):
        add_new_transaction(
            account_repository=account_repository,
            account=account2,
            transaction_id=tr_id,
            amount=Money(Decimal(10)),
        )
