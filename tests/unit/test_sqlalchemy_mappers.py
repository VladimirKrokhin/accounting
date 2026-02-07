import pytest
from decimal import Decimal
from uuid import uuid4

from adapters.sqlalchemy.mappers import (
    AccountMapper,
    PaymentEntryMapper,
)
from adapters.sqlalchemy.models import (
    Account as SQLAlchemyAccount,
    PaymentEntry as SQLAlchemyPaymentEntry,
)
from domain.models import (
    Money,
    AccountId,
    PaymentEntryId,
    UserId,
    Account,
)


@pytest.fixture
def sample_ids():
    return {"payment": uuid4(), "transaction": uuid4(), "user": 42, "account": 1}


def test_payment_to_domain(sample_ids):
    orm_payment = SQLAlchemyPaymentEntry(
        id=sample_ids["payment"],
        transaction_id=sample_ids["transaction"],
        account_id=sample_ids["account"],
        amount=Money(Decimal("150.00")),
        is_accrued=True,
    )

    domain_payment = PaymentEntryMapper.to_domain(orm_payment)

    assert domain_payment.id_ == PaymentEntryId(sample_ids["payment"])
    assert domain_payment.amount == Money(Decimal("150.00"))


def test_account_to_domain_mapping(sample_ids):
    """Проверка проброса user_id"""
    orm_account = SQLAlchemyAccount(
        id=sample_ids["account"],
        user_id=sample_ids["user"],  # FK на account_user.id
        balance=Money(Decimal("1000.00")),
        payments=[],
    )

    domain_account = AccountMapper.to_domain(orm_account)

    assert domain_account.id_ == AccountId(sample_ids["account"])
    assert domain_account.user_id == UserId(sample_ids["user"])  # Проверяем связь


def test_account_to_orm_mapping(sample_ids):
    """Проверка обратного маппинга user_id -> account_user_id"""
    domain_account = Account(
        id_=AccountId(sample_ids["account"]),
        user_id=UserId(sample_ids["user"]),
        balance=Money(Decimal("1000.00")),
        payments=set(),
    )

    orm_account = AccountMapper.to_orm(domain_account)

    assert orm_account.id == sample_ids["account"]
    assert orm_account.user_id == sample_ids["user"]
    assert Money(orm_account.balance) == Money(Decimal("1000.00"))


def test_account_mapping_with_payments(sample_ids):
    """Проверка маппинга вложенных сущностей (платежей)"""
    orm_payment = SQLAlchemyPaymentEntry(
        id=sample_ids["payment"],
        transaction_id=sample_ids["transaction"],
        amount=Money(Decimal("50.00")),
        is_accrued=False,
    )
    orm_account = SQLAlchemyAccount(
        id=sample_ids["account"],
        user_id=sample_ids["user"],
        balance=Money(Decimal("500.00")),
        payments=[orm_payment],
    )

    domain_account = AccountMapper.to_domain(orm_account)

    assert len(domain_account.payments) == 1
    payment_in_account = list(domain_account.payments)[0]
    assert payment_in_account.id_ == PaymentEntryId(sample_ids["payment"])
