from dataclasses import dataclass, field
from decimal import Decimal

from accounts.domain.exceptions import (
    PaymentEntryAlreadyAccrued,
    PaymentEntryDoesNotExistsError,
    PaymentEntryIsNotUniqueError,
)
from accounts.domain.types import (
    AccountId,
    Money,
    PaymentEntryId,
    TransactionId,
    UserId,
    next_payment_entry_id,
)


@dataclass
class PaymentEntry:
    """Платеж."""

    id_: PaymentEntryId
    transaction_id: TransactionId
    account_id: AccountId | None
    amount: Money
    is_accrued: bool = False  # Зачислен на счет?

    def __hash__(self) -> int:
        return hash(self.transaction_id)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, PaymentEntry):
            return False

        return self.transaction_id == value.transaction_id


@dataclass
class Account:
    """Счет."""

    user_id: UserId
    balance: Money = Money(Decimal(0))

    payments: set[PaymentEntry] = field(default_factory=set)
    id_: AccountId | None = None

    def add_payment_entry(
        self,
        transaction_id: TransactionId,
        amount: Money,
    ) -> PaymentEntryId:
        """Добавить платеж."""

        pe_id = next_payment_entry_id()

        entry = PaymentEntry(
            id_=pe_id,
            transaction_id=transaction_id,
            account_id=AccountId(self.id_) if self.id_ is not None else None,
            amount=amount,
            is_accrued=False,  # Еще не зачислен
        )

        # Бизнес-правило: транзакции являются уникальными, начисление суммы с одним transaction_id должно производиться только один раз.
        if entry in self.payments:
            raise PaymentEntryIsNotUniqueError(
                "Значение transaction_id не является уникальным"
            )

        self.payments.add(entry)
        entry.account_id = self.id_

        return pe_id

    def accrue_payment_entry(self, pe_id: PaymentEntryId) -> None:
        """
        Начислить платеж на счет пользователя.
        """

        for p in self.payments:
            if pe_id == p.id_:
                payment = p
                break
        else:
            raise PaymentEntryDoesNotExistsError(
                "Не найден платеж с указанным идентификатором"
            )

        # Бизнес-правило: транзакции являются уникальными, начисление суммы с одним transaction_id должно производиться только один раз.
        if payment.is_accrued:
            raise PaymentEntryAlreadyAccrued("Платеж уже начислен")

        self.balance += payment.amount  # pyright: ignore[reportAttributeAccessIssue]
        payment.is_accrued = True

    def __hash__(self) -> int:
        return hash(self.id_)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Account):
            return False

        return self.id_ == value.id_
