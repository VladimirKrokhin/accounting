import pytest
from domain import TransactionId, Account, Money, UserId, AccountId
from infrastructure.repository import FakeAccountRepository
from services.payment_system import add_new_transaction


def test_add_new_transaction_success():
    repository = FakeAccountRepository()
    account = Account(id_=AccountId(1), user_id=UserId(1), balance=Money(1))
    tr_id = TransactionId("23")

    pe_id = add_new_transaction(
        repository=repository,
        account=account,
        transaction_id=tr_id,
        amount=Money(100),
    )

    # Платеж добавлен
    assert len(account.payments) == 1

    # Баланс не изменен
    assert account.balance == Money(1)

    # Платеж не начислен
    p = tuple(account.payments)[0]
    assert p.is_accrued == False
    assert p.account_id == account.id_
