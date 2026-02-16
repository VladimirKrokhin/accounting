from abc import ABCMeta
from dataclasses import dataclass, field
from datetime import timedelta
from enum import StrEnum

from accounts.core.types import TransactionId, UserId, AccountId, Money


class UserType(StrEnum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class UserDTO:
    email: str
    full_name: str
    user_type: UserType
    password_hash: str = field(repr=False)

    user_id: UserId | None = None


@dataclass(frozen=True)
class CreateOrUpdateUserDTO:
    email: str
    full_name: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class AccountDTO(metaclass=ABCMeta):
    pass


# Обработка вебхуков от платежной системы


@dataclass(frozen=True)
class HandlePaymentSystemTransactionDTO(AccountDTO):
    """Обработать транзакцию от платежной системы."""

    transaction_id: TransactionId
    user_id: UserId
    account_id: AccountId
    amount: Money
    signature: str


# Операция с пользователями


@dataclass(frozen=True)
class CreateUserDTO(AccountDTO):
    """Создать пользователя."""

    email: str
    full_name: str
    password: str


@dataclass(frozen=True)
class UpdateUserDTO(AccountDTO):
    """Обновить пользователя."""

    user_id: UserId
    email: str
    full_name: str
    password: str


@dataclass(frozen=True)
class DeleteUserDTO(AccountDTO):
    """Удалить пользователя."""

    user_id: id
