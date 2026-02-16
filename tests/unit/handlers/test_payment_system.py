from decimal import Decimal
from uuid import UUID

from accounts.dtos import UserDTO, UserType
from accounts.domain.models import Account, AccountId, Money, TransactionId, UserId
from accounts.domain.messages import HandlePaymentSystemTransaction
from accounts.adapters.repository import (
    FakeAccountRepository,
    FakeUserRepository,
)
from accounts.service_layer.handlers.payment_system import (
    process_payment_system_transaction,
)
from accounts.service_layer.unit_of_work import FakeUnitOfWork


def test_process_payment_system_transaction_success_user_has_account():
    secret = "gfdmhghif38yrf9ew0jkf32"
    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"

    transaction_id = TransactionId(UUID("5eae174f-7cd0-472c-bd36-35660f00132b"))
    user_id = UserId(1)
    account_id = AccountId(1)
    amount = Money(Decimal(100))
    start_balance = Money(Decimal(0))

    account_repository = FakeAccountRepository()
    user_repository = FakeUserRepository()

    account = Account(
        id_=account_id,
        user_id=user_id,
        balance=start_balance,
    )
    user = UserDTO(
        email="test@user.example",
        full_name="Test User",
        password_hash="hash",
        user_id=user_id,
        user_type=UserType.USER,
    )
    account_repository.save_account(account)
    user_repository.save_user(user)
    uow = FakeUnitOfWork(users=user_repository, accounts=account_repository)

    message = HandlePaymentSystemTransaction(
        transaction_id=transaction_id,
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        signature=signature,
        secret_key=secret,
    )

    process_payment_system_transaction(message=message, uow=uow)

    account = account_repository.get_account_by_id(account_id)

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

    transaction_id = TransactionId(UUID("5eae174f-7cd0-472c-bd36-35660f00132b"))
    start_balance = Money(Decimal(0))
    user_id = UserId(1)
    amount = Money(Decimal(100))
    account_id = AccountId(1)

    account_repository = FakeAccountRepository()
    user_repository = FakeUserRepository({}, 1)

    user = UserDTO(
        email="test@user.example",
        full_name="Test User",
        password_hash="hash",
        user_id=user_id,
        user_type=UserType.USER,
    )
    user_repository.save_user(user)

    uow = FakeUnitOfWork(users=user_repository, accounts=account_repository)

    message = HandlePaymentSystemTransaction(
        transaction_id=transaction_id,
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        signature=signature,
        secret_key=secret,
    )

    # Счета нет
    assert not account_repository.is_user_has_account(
        user_id=user_id, account_id=account_id
    )

    process_payment_system_transaction(message=message, uow=uow)

    account = account_repository.get_account_by_id(account_id)

    # Платеж появился на счете
    assert len(account.payments) == 1
    # Счет имеет значение суммы платежа
    assert account.balance == amount

    p = tuple(account.payments)[0]
    # Платеж имеет необходимый transaction_id
    assert p.transaction_id == transaction_id
    # Платеж указан начисленным
    assert p.is_accrued == True


# TODO: Добавь тест: создается/не создается новый аккаунт
