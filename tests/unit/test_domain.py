import pytest

from domain import (
    Account,
    AccountId,
    PaymentEntry,
    PaymentEntryAlreadyAccrued,
    PaymentEntryDoesNotExistsError,
    PaymentEntryIsNotUniqueError,
    TransactionId,
    PaymentEntryId,
    UserId,
    Money,
)


def test_account_add_payment_success():
    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(1),
    )

    # Проверяем, что платежей на счете нет
    assert len(account.payments) == 0

    pe_id = account.add_payment_entry(
        transaction_id=TransactionId("232"),
        amount=Money(100),
    )

    # Платеж появился
    assert len(account.payments) == 1

    # Пока не отражается на балансе, если его не начислить
    assert account.balance == Money(1)

    pe = tuple(account.payments)[0]

    # Все поля совпадают
    assert pe.id_ == pe_id
    assert pe.transaction_id == TransactionId("232")
    assert pe.amount == Money(100)
    assert pe.account_id == account.id_


def test_account_accrue_payment_success():
    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(1),
    )

    pe_id = account.add_payment_entry(
        transaction_id=TransactionId("232"),
        amount=Money(100),
    )

    # Не отмечен как начисленный
    pe = tuple(account.payments)[0]
    assert pe.is_accrued == False

    account.accrue_payment_entry(pe_id)

    # Отражается на балансе
    assert account.balance == Money(101)
    # Отмечен как начисленный
    pe = tuple(account.payments)[0]
    assert pe.is_accrued == True


def test_account_add_payment_unique_violation():
    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(1),
    )

    tr_id = TransactionId("232")
    account.add_payment_entry(
        transaction_id=tr_id,
        amount=Money(100),
    )

    with pytest.raises(PaymentEntryIsNotUniqueError):
        account.add_payment_entry(
            transaction_id=tr_id,
            amount=Money(200),
        )


def test_account_accrue_payment_already_accrued():

    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(1),
    )

    pe_id = account.add_payment_entry(
        transaction_id=TransactionId("232"),
        amount=Money(100),
    )

    account.accrue_payment_entry(pe_id)

    with pytest.raises(PaymentEntryAlreadyAccrued):
        account.accrue_payment_entry(pe_id)


def test_account_accrue_payment_does_not_exists():

    account = Account(
        id_=AccountId(1),
        user_id=UserId(1),
        balance=Money(1),
    )

    pe_id = PaymentEntryId(1)

    with pytest.raises(PaymentEntryDoesNotExistsError):
        account.accrue_payment_entry(pe_id)
