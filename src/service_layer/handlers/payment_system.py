from decimal import Decimal
import hashlib
from typing import TYPE_CHECKING

from domain.exceptions import PaymentEntryIsNotUniqueError
from domain.types import (
    AccountId,
    PaymentEntryId,
    Money,
    UserId,
)
from domain.models import Account
from domain.messages import HandlePaymentSystemTransaction
from domain.exceptions import SignatureIsNotValid, UserDoesNotExists
from adapters.repository import (
    AbstractAccountRepository,
)
from service_layer.unit_of_work import AbstractUnitOfWork

if TYPE_CHECKING:
    from domain.types import (
        AccountId,
        TransactionId,
    )

__all__ = ["process_payment_system_transaction"]


def validate_transaction_signature(
    signature: str,
    transaction_id: TransactionId,
    account_id: AccountId,
    user_id: UserId,
    amount: Money,
    secret_key: str,
) -> None:
    """Проверить подпись транзакции.

    Подпись формируется через SHA256 хеш,
    для строки состоящей из конкатенации значений объекта
    в алфавитном порядке ключей и “секретного ключа”,
    хранящегося в конфигурации проекта
    ({account_id}{amount}{transaction_id}{user_id}{secret_key}).

    Пример, для secret_key gfdmhghif38yrf9ew0jkf32:
    {
      "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
      "user_id": 1,
      "account_id": 1,
      "amount": 100,
      "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    }
    """

    signature_string = f"{account_id}{amount}{transaction_id}{user_id}{secret_key}"
    signature_hasher = hashlib.sha256()
    signature_hasher.update(signature_string.encode())
    signature_hash = signature_hasher.hexdigest()

    is_valid = signature_hash == signature
    if not is_valid:
        raise SignatureIsNotValid


def add_new_transaction(
    account_repository: AbstractAccountRepository,
    account: Account,
    transaction_id: TransactionId,
    amount: Money,
) -> tuple[AccountId, PaymentEntryId]:
    """
    Добавить новую транзакцию к счету. Не начисляет средства на баланс.
    """

    is_duplicate = account_repository.is_payment_entry_exists_by_transaction_id(
        transaction_id=transaction_id
    )

    if is_duplicate:
        raise PaymentEntryIsNotUniqueError("Транзакция дублируется")

    pe_id = account.add_payment_entry(
        transaction_id=transaction_id,
        amount=amount,
    )

    acc_id = account_repository.save_account(account)

    return (acc_id, pe_id)


def process_payment_system_transaction(
    message: HandlePaymentSystemTransaction,
    uow: AbstractUnitOfWork,
) -> tuple[AccountId, PaymentEntryId, bool]:
    """
    Обработать транзакцию от платежной системы.


    При обработке:
    1. Проверяет подпись объекта
    2. Проверяет существует ли у пользователя такой счет - если нет, его необходимо создать
    3. Сохраняет транзакцию в базе данных
    4. Начисляет сумму транзакции на счет пользователя
    """

    # Обработать транзакцию от платежной системы.

    transaction_id = message.transaction_id
    user_id = message.user_id
    account_id = message.account_id
    amount = message.amount
    signature = message.signature
    payment_system_secret_key = message.secret_key

    user_repository = uow.users
    account_repository = uow.accounts

    # 1. Проверить подпись объекта
    validate_transaction_signature(
        signature=signature,
        transaction_id=transaction_id,
        account_id=account_id,
        user_id=user_id,
        amount=amount,
        secret_key=payment_system_secret_key,
    )

    # Проверим, существует ли пользователь.
    is_user_exists = user_repository.is_user_exists(user_id)
    if not is_user_exists:
        raise UserDoesNotExists("Пользователь с указанным user_id не существует")

    # 2. Проверить существует ли у пользователя такой счет - если нет, его необходимо создать
    is_user_has_account: bool = account_repository.is_user_has_account(
        user_id=user_id, account_id=account_id
    )

    if not is_user_has_account:
        account = Account(
            id_=account_id,
            balance=Money(Decimal(0)),
            user_id=user_id,
        )
        account_id = account_repository.save_account(account)

    # Был ли создан счет?
    is_account_created = not is_user_has_account

    # 3. Сохранить транзакцию в базе данных
    account = account_repository.get_account_by_id(account_id=account_id)
    account_id, pe_id = add_new_transaction(
        account_repository=account_repository,
        account=account,
        transaction_id=transaction_id,
        amount=amount,
    )

    # 4. Начислить сумму транзакции на счет пользователя
    account = account_repository.get_account_by_id(account_id)
    account.accrue_payment_entry(pe_id)
    account_id = account_repository.save_account(account)

    return account_id, pe_id, is_account_created
