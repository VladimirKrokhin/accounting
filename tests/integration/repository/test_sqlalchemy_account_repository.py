import pytest
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from accounts.core.entities import Account
from accounts.core.types import AccountId, Money, TransactionId, UserId
from accounts.adapters.repository import SQLAlchemyAccountRepository
from accounts.adapters.sqlalchemy.models import Base


@pytest.fixture(scope="function")
def engine():
    # Используем SQLite в памяти для тестов
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def repository(session):
    return SQLAlchemyAccountRepository(session)


def test_repository_can_save_and_retrieve_account(repository, session):
    user_id = UserId(101)
    # Создаем счет
    account = Account(
        user_id=user_id,
        balance=Money(Decimal("100.00")),
    )

    # Сохраняем
    account_id = repository.save_account(account)
    session.commit()

    # Получаем обратно
    retrieved_account = repository.get_account_by_id(account_id)

    assert retrieved_account.id_ == account_id
    assert retrieved_account.user_id == user_id
    assert retrieved_account.balance == Decimal("100.00")

    # Проверяем, отражается ли у пользователя
    user_accounts = repository.get_user_accounts(user_id)
    assert len(user_accounts) == 1

    retrieved_user_account = user_accounts[0]
    assert retrieved_user_account.id_ == account_id
    assert retrieved_user_account.user_id == user_id
    assert retrieved_user_account.balance == Decimal("100.00")


def test_repository_can_save_account_with_payments(repository, session):
    user_id = UserId(1)
    initial_balance = Money(Decimal("0.00"))
    account = Account(user_id=user_id, balance=initial_balance)
    # Сохраняем
    account_id = repository.save_account(account)
    # session.commit()

    tx_id = TransactionId(uuid4())
    transaction_amount = Money(Decimal("50.00"))
    pe_id = account.add_payment_entry(transaction_id=tx_id, amount=transaction_amount)

    repository.save_account(account)
    # session.commit()

    # Получаем обратно
    retrieved_account = repository.get_account_by_id(account_id)
    assert retrieved_account.user_id == user_id
    assert retrieved_account.balance == Money(Decimal("0.00"))
    payment = tuple(retrieved_account.payments)[0]
    assert payment.amount == transaction_amount
    assert payment.transaction_id == tx_id
    assert payment.id_ == pe_id
    assert payment.account_id == account_id

    # Проверяем, отражается ли у пользователя
    user_accounts = repository.get_user_accounts(user_id)
    assert len(user_accounts) == 1

    retrieved_user_account = user_accounts[0]
    assert retrieved_user_account.id_ == account_id
    assert retrieved_user_account.user_id == user_id
    assert retrieved_user_account.balance == Decimal("0.00")
    user_account_payment = tuple(retrieved_account.payments)[0]
    assert user_account_payment.amount == transaction_amount
    assert user_account_payment.transaction_id == tx_id
    assert user_account_payment.id_ == pe_id
    assert user_account_payment.account_id == account_id

    user_payments = repository.get_user_payments(user_id)
    user_payment = user_payments[0]
    assert user_payment.amount == transaction_amount
    assert user_payment.transaction_id == tx_id
    assert user_payment.id_ == pe_id
    assert user_payment.account_id == account_id


def test_is_payment_entry_exists_by_transaction_id(repository, session):
    tx_id = TransactionId(uuid4())
    account = Account(user_id=UserId(1), balance=Money(Decimal("0.00")))
    account.add_payment_entry(transaction_id=tx_id, amount=Money(Decimal("10.00")))

    repository.save_account(account)
    session.commit()

    assert repository.is_payment_entry_exists_by_transaction_id(tx_id) is True
    assert (
        repository.is_payment_entry_exists_by_transaction_id(TransactionId(uuid4()))
        is False
    )


def test_is_user_has_account(repository, session):
    uid = UserId(55)
    account = Account(user_id=uid)
    acc_id = repository.save_account(account)
    session.commit()

    assert repository.is_user_has_account(uid, acc_id) is True
    assert repository.is_user_has_account(UserId(999), acc_id) is False


def test_save_account_updates_existing_balance(repository, session):
    # Создаем
    account = Account(user_id=UserId(1), balance=Money(Decimal("100.00")))
    acc_id = repository.save_account(account)
    session.commit()

    # Изменяем баланс
    account.id_ = acc_id
    account.balance = Money(Decimal("250.00"))

    # Сохраняем обновление
    repository.save_account(account)
    session.commit()

    # Проверяем
    session.expire_all()
    retrieved = repository.get_account_by_id(acc_id)
    assert retrieved.balance == Decimal("250.00")


def test_get_account_by_id_raises_error_if_not_found(repository):
    with pytest.raises(ValueError, match="не найден"):
        repository.get_account_by_id(AccountId(9999))


def test_is_account_exists(repository, session):
    account = Account(user_id=UserId(1))
    acc_id = repository.save_account(account)
    session.commit()

    assert repository.is_account_exists(acc_id) is True
    assert repository.is_account_exists(AccountId(9999)) is False
