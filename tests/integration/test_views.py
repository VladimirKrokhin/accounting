from decimal import Decimal
import pytest
from adapters.repository import FakeAccountRepository, FakeUserRepository
from bootstrap import bootstrap
from domain.models import Account, PaymentEntry, UserId, AccountId
from domain.exceptions import UserDoesNotExists
from domain.types import Money, TransactionId, next_payment_entry_id
from dtos import UserDTO, UserType
from service_layer.message_bus import MessageBus
from service_layer.unit_of_work import FakeUnitOfWork
from views import get_user_accounts, get_user_data, get_user_payments, get_users


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
    user_repo = FakeUserRepository({user_id: user}, 1)

    # Создаем счет и платеж для этого пользователя
    payment = PaymentEntry(
        transaction_id=TransactionId("tx1"),
        amount=Money(Decimal(100)),
        id_=next_payment_entry_id(),
        account_id=AccountId(1),
    )
    account = Account(id_=AccountId(1), user_id=user_id, payments=[payment])

    account_repo = FakeAccountRepository({account.id_: account}, 1)
    account_repo.save_account(account)

    uow = FakeUnitOfWork(users=user_repo, accounts=account_repo)
    mb = bootstrap(uow=uow)

    return user_id, mb


## --- Тесты get_user_accounts ---


def test_get_user_accounts_returns_correct_list(setup_data):
    user_id, mb = setup_data
    uow = mb.uow
    account_repo, user_repo = uow.accounts, uow.users

    accounts = get_user_accounts(user_id, account_repo, user_repo)

    assert len(accounts) == 1
    assert accounts[0].user_id == user_id
    assert accounts[0].id_ == AccountId(1)


def test_get_user_accounts_raises_if_user_missing(setup_data):
    _, mb = setup_data
    uow = mb.uow
    account_repo, user_repo = uow.accounts, uow.users

    with pytest.raises(UserDoesNotExists):
        get_user_accounts(UserId(999), account_repo, user_repo)


## --- Тесты get_user_payments ---


def test_get_user_payments_success(setup_data):
    user_id, mb = setup_data
    uow = mb.uow
    account_repo, user_repo = uow.accounts, uow.users

    payments = get_user_payments(user_id, account_repo, user_repo)

    assert len(payments) == 1
    assert payments[0].transaction_id == "tx1"


## --- Тесты get_user_data ---


def test_get_user_data_returns_dto(setup_data):
    user_id, mb = setup_data
    uow = mb.uow
    user_repo = uow.users
    user_dto = get_user_data(user_id, user_repo)

    assert user_dto.user_id == user_id
    assert user_dto.full_name == "Alice"


## --- Тесты get_users ---


def test_get_users_returns_all(setup_data):
    _, mb = setup_data
    uow = mb.uow
    user_repo = uow.users

    all_users = get_users(user_repo)

    assert len(all_users) == 1
    assert all_users[0].full_name == "Alice"
