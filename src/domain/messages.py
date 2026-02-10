from abc import ABCMeta
from dataclasses import dataclass
from datetime import timedelta

from domain.types import TransactionId, UserId, AccountId, Money


@dataclass(frozen=True)
class Message(metaclass=ABCMeta):
    pass


# Обработка вебхуков от платежной системы


@dataclass(frozen=True)
class HandlePaymentSystemTransaction(Message):
    """Обработать транзакцию от платежной системы."""

    transaction_id: TransactionId
    user_id: UserId
    account_id: AccountId
    amount: Money
    signature: str
    secret_key: str


# Операция с пользователями


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
