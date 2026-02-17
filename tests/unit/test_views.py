from decimal import Decimal
from uuid import uuid4
import pytest


from accounts.core.entities import Account, PaymentEntry
from accounts.core.types import (
    UserId,
    AccountId,
    Money,
    TransactionId,
    next_payment_entry_id,
)

from accounts.core.exceptions import UserDoesNotExists
from accounts.dtos import UserDTO, UserType
from accounts.views import (
    get_user_accounts,
    get_user_data,
    get_user_payments,
    get_users,
)
from fakes import FakeAccountRepository, FakeUserRepository, FakeUnitOfWork

tr_id = TransactionId(uuid4())


@pytest.fixture
def setup_data():
    """Фикстура для инициализации репозиториев данными."""
    user_id = UserId(1)

    # Создаем тестового пользователя
    user = UserDTO(
        user_id=user_id,
        full_name="Alice",
        user_type=UserType.USER,
        email="alice@in.wondlerland",
        password_hash="sadfadf",
    )
    user_repo = FakeUserRepository(user)

    # Создаем счет и платеж для этого пользователя
    payment = PaymentEntry(
        transaction_id=tr_id,
        amount=Money(Decimal(100)),
        id_=next_payment_entry_id(),
        account_id=AccountId(1),
    )
    account = Account(id_=AccountId(1), user_id=user_id, payments={payment})

    account_repo = FakeAccountRepository(account)
    uow = FakeUnitOfWork(users=user_repo, accounts=account_repo)

    return user_id, uow


## --- Тесты get_user_accounts ---


@pytest.mark.asyncio
async def test_get_user_accounts_returns_correct_list(setup_data):
    user_id, uow = setup_data

    accounts = await get_user_accounts(user_id, uow)

    assert len(accounts) == 1
    assert accounts[0].user_id == user_id
    assert accounts[0].id_ == AccountId(1)


@pytest.mark.asyncio
async def test_get_user_accounts_raises_if_user_missing(setup_data):
    _, uow = setup_data

    with pytest.raises(UserDoesNotExists):
        await get_user_accounts(UserId(999), uow)


## --- Тесты get_user_payments ---


@pytest.mark.asyncio
async def test_get_user_payments_success(setup_data):
    user_id, uow = setup_data

    payments = await get_user_payments(user_id, uow)

    assert len(payments) == 1
    assert payments[0].transaction_id == tr_id


## --- Тесты get_user_data ---


@pytest.mark.asyncio
async def test_get_user_data_returns_dto(setup_data):
    user_id, uow = setup_data
    user_dto = await get_user_data(user_id, uow)

    assert user_dto.user_id == user_id
    assert user_dto.full_name == "Alice"


## --- Тесты get_users ---


@pytest.mark.asyncio
async def test_get_users_returns_all(setup_data):
    _, uow = setup_data

    all_users = await get_users(uow)

    assert len(all_users) == 1
    assert all_users[0].full_name == "Alice"
