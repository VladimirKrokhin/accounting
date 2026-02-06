from abc import ABCMeta
from dataclasses import dataclass
from domain.models import TransactionId, UserId, AccountId, Money


@dataclass(frozen=True)
class Message(metaclass=ABCMeta):
    pass


@dataclass(frozen=True)
class HandlePaymentSystemTransaction(Message):
    """DTO для обработки транзакции от платежной системы."""

    transaction_id: TransactionId
    user_id: UserId
    account_id: AccountId
    amount: Money
    signature: str
