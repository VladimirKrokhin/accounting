from decimal import Decimal
from typing import NewType
import uuid

AccountId = NewType(name="AccountId", tp=int)
UserId = NewType(name="UserId", tp=int)
PaymentEntryId = NewType(name="PaymentEntryId", tp=uuid.UUID)
TransactionId = NewType(name="TransactionId", tp=uuid.UUID)

Money = NewType(name="Money", tp=Decimal)


def next_payment_entry_id():
    return PaymentEntryId(uuid.uuid4())
