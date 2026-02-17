from decimal import Decimal
from typing import List
from typing import Optional

from sqlalchemy import UUID, Boolean, ForeignKey, Numeric, Uuid
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


# Пользователи


class User(Base):
    """
    Общая сущность пользователя.
    """

    __tablename__ = "base_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    email_address: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    type: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "base_user",
        "polymorphic_on": "type",
    }

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email_address='{self.email_address!r}', fullname='{self.full_name!r}')"


class AccountsUser(User):
    """Сущность бизнес-пользователя (для работы со счетами)."""

    __tablename__ = "account_user"

    id: Mapped[int] = mapped_column(ForeignKey("base_user.id"), primary_key=True)
    accounts: Mapped[List["Account"]] = relationship(back_populates="user")

    __mapper_args__ = {
        "polymorphic_identity": "user",
    }

    def __repr__(self) -> str:
        return f"AccountsUser(id={self.id!r}, email_address='{self.email_address!r}')"


class Administrator(User):
    """
    Сущность администратора.
    """

    __tablename__ = "admin_user"

    id: Mapped[int] = mapped_column(ForeignKey("base_user.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

    def __repr__(self) -> str:
        return f"Administrator(id={self.id!r}, email_address='{self.email_address!r}')"


# Счета и транзакции


class Account(Base):
    """
    Сущность счета - баланса, привязанного к пользователю.
    """

    __tablename__ = "account"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("base_user.id"))
    balance: Mapped[Decimal] = mapped_column(Numeric())

    user: Mapped["AccountsUser"] = relationship(back_populates="accounts")
    payments: Mapped[List["PaymentEntry"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Account(id={self.id!r}, user_id={self.user_id!r})"


class PaymentEntry(Base):
    """
    Сущность платежа (пополнения баланса).
    """

    __tablename__ = "payment_entry"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    transaction_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric())
    is_accrued: Mapped[bool] = mapped_column(Boolean())

    account: Mapped["Account"] = relationship(back_populates="payments")

    def __repr__(self) -> str:
        return f"PaymentEntry(id={self.id!r}, transaction_id={self.transaction_id!r}, account_id={self.account_id!r})"
