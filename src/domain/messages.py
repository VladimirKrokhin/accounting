from abc import ABCMeta
from dataclasses import dataclass
from domain.models import TransactionId, UserId, AccountId, Money


@dataclass(frozen=True)
class Message(metaclass=ABCMeta):
    pass


@dataclass(frozen=True)
class HandlePaymentSystemTransaction(Message):
    """Обработать транзакцию от платежной системы."""

    transaction_id: TransactionId
    user_id: UserId
    account_id: AccountId
    amount: Money
    signature: str


@dataclass(frozen=True)
class CreateUser(Message):
    """Создать пользователя."""

    email: str
    full_name: str
    password: str


@dataclass(frozen=True)
class UpdateUser(Message):
    """Обновить пользователя."""

    user_id: UserId
    email: str
    full_name: str
    password: str


@dataclass(frozen=True)
class DeleteUser(Message):
    """Удалить пользователя."""

    user_id: id
