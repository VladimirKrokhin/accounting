from decimal import Decimal
from uuid import uuid4
import pytest

from accounts.domain.exceptions import (
    PaymentEntryAlreadyAccrued,
    PaymentEntryDoesNotExistsError,
    PaymentEntryIsNotUniqueError,
)
from accounts.domain.models import (
    Account,
    AccountId,
    TransactionId,
    UserId,
    Money,
    next_payment_entry_id,
)


def test_account_add_payment_success():
    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(Decimal(1)),
    )

    # Проверяем, что платежей на счете нет
    assert len(account.payments) == 0
    tr_id = TransactionId(uuid4())

    pe_id = account.add_payment_entry(
        transaction_id=tr_id,
        amount=Money(Decimal(100)),
    )

    # Платеж появился
    assert len(account.payments) == 1

    # Пока не отражается на балансе, если его не начислить
    assert account.balance == Money(Decimal(1))

    pe = tuple(account.payments)[0]

    # Все поля совпадают
    assert pe.id_ == pe_id
    assert pe.transaction_id == tr_id
    assert pe.amount == Money(Decimal(100))
    assert pe.account_id == account.id_


def test_account_accrue_payment_success():
    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(Decimal(1)),
    )

    pe_id = account.add_payment_entry(
        transaction_id=TransactionId(uuid4()),
        amount=Money(Decimal(100)),
    )

    # Не отмечен как начисленный
    pe = tuple(account.payments)[0]
    assert pe.is_accrued == False

    account.accrue_payment_entry(pe_id)

    # Отражается на балансе
    assert account.balance == Money(Decimal(101))
    # Отмечен как начисленный
    pe = tuple(account.payments)[0]
    assert pe.is_accrued == True


def test_account_add_payment_unique_violation():
    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(Decimal(1)),
    )

    tr_id = TransactionId(uuid4())
    account.add_payment_entry(
        transaction_id=tr_id,
        amount=Money(Decimal(100)),
    )

    with pytest.raises(PaymentEntryIsNotUniqueError):
        account.add_payment_entry(
            transaction_id=tr_id,
            amount=Money(Decimal(200)),
        )


def test_account_accrue_payment_already_accrued():

    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(Decimal(1)),
    )

    pe_id = account.add_payment_entry(
        transaction_id=TransactionId(uuid4()),
        amount=Money(Decimal(100)),
    )

    account.accrue_payment_entry(pe_id)

    with pytest.raises(PaymentEntryAlreadyAccrued):
        account.accrue_payment_entry(pe_id)


def test_account_accrue_payment_does_not_exists():

    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(Decimal(1)),
    )

    pe_id = next_payment_entry_id()

    with pytest.raises(PaymentEntryDoesNotExistsError):
        account.accrue_payment_entry(pe_id)
