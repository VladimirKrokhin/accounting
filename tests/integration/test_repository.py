import pytest
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.models import Account, AccountId, Money, TransactionId, UserId
from adapters.repository import SQLAlchemyAccountRepository
from adapters.sqlalchemy.models import Base


@pytest.fixture
def engine():
    # Используем SQLite в памяти для тестов
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def repository(session):
    return SQLAlchemyAccountRepository(session)


def test_repository_can_save_and_retrieve_account(repository, session):
    user_id = UserId(101)
    # Создаем доменный объект
    account = Account(
        user_id=user_id,
        balance=Money(Decimal("100.00")),
    )

    # 1. Сохраняем (внутри происходит to_orm и session.merge)
    account_id = repository.save_account(account)
    session.commit()

    # 2. Получаем обратно
    retrieved_account = repository.get_account_by_id(account_id)

    assert retrieved_account.id_ == account_id
    assert retrieved_account.user_id == user_id
    assert retrieved_account.balance == Decimal("100.00")


def test_repository_can_save_account_with_payments(repository, session):
    account = Account(user_id=UserId(1), balance=Money(Decimal("0.00")))
    # Сохраняем и ОБЯЗАТЕЛЬНО присваиваем полученный ID обратно в домен
    account.id_ = repository.save_account(account)
    session.commit()

    # Теперь при добавлении платежа entry.account_id будет равен 1, а не None
    tx_id = TransactionId(uuid4())
    account.add_payment_entry(transaction_id=tx_id, amount=Money(Decimal("50.00")))

    repository.save_account(account)
    session.commit()


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

    # Изменяем баланс в домене
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
