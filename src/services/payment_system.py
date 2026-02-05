from dataclasses import dataclass
import hashlib
from infrastructure.repository import FakeAccountRepository
from domain import (
    AccountId,
    PaymentEntryIsNotUniqueError,
    TransactionId,
    PaymentEntryId,
    Money,
    Account,
    UserId,
)


class SignatureIsNotValid(Exception):
    pass


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
    repository: FakeAccountRepository,
    account: Account,
    transaction_id: TransactionId,
    amount: Money,
) -> PaymentEntryId:
    """
    Добавить новую транзакцию к счету. Не начисляет средства на баланс.
    """

    is_duplicate = repository.is_payment_entry_exists_by_transaction_id(transaction_id)

    if is_duplicate:
        raise PaymentEntryIsNotUniqueError("Транзакция дублируется")

    pe_id = account.add_payment_entry(
        transaction_id=transaction_id,
        amount=amount,
    )

    return pe_id


@dataclass(frozen=True)
class HandlePaymentSystemTransactionDto:
    """DTO для обработки транзакции от платежной системы."""

    transaction_id: TransactionId
    user_id: UserId
    account_id: AccountId
    amount: Money
    signature: str


def process_payment_system_transaction(
    repository: FakeAccountRepository,
    transaction: HandlePaymentSystemTransactionDto,
    secret: str,
) -> tuple[AccountId, PaymentEntryId]:
    """
    Обработать транзакцию от платежной системы.


    При обработке:
    1. Проверяет подпись объекта
    2. Проверяет существует ли у пользователя такой счет - если нет, его необходимо создать
    3. Сохраняет транзакцию в базе данных
    4. Начисляет сумму транзакции на счет пользователя
    """

    # Обработать транзакцию от платежной системы.

    transaction_id = transaction.transaction_id
    user_id = transaction.user_id
    account_id = transaction.account_id
    amount = transaction.amount
    signature = transaction.signature

    # 1. Проверить подпись объекта
    validate_transaction_signature(
        signature=signature,
        transaction_id=transaction_id,
        account_id=account_id,
        user_id=user_id,
        amount=amount,
        secret_key=secret,
    )

    # 2. Проверить существует ли у пользователя такой счет - если нет, его необходимо создать
    is_user_has_account: bool = repository.is_user_has_account(
        user_id=user_id, account_id=account_id
    )

    if not is_user_has_account:
        account = Account(
            id_=account_id,
            balance=Money(0),
            user_id=user_id,
        )
        account_id = repository.save_account(account)

    account = repository.get_account_by_id(account_id=account_id)

    # 3. Сохранить транзакцию в базе данных
    pe_id = add_new_transaction(
        repository=repository,
        account=account,
        transaction_id=transaction_id,
        amount=amount,
    )
    account_id = repository.save_account(account)

    # 4. Начислить сумму транзакции на счет пользователя
    account.accrue_payment_entry(pe_id)
    account_id = repository.save_account(account)

    return account_id, pe_id
