from abc import ABCMeta, abstractmethod

from sqlalchemy import exists, select
from sqlalchemy.orm import Session
from domain.models import Account, AccountId, PaymentEntry, UserId, TransactionId
from adapters.sqlalchemy.mappers import (
    AccountMapper,
    PaymentEntryMapper,
    SQLAlchemyAccount,
    SQLAlchemyPaymentEntry,
)
from dtos import UserDTO


class UserDoesNotExists(Exception):
    pass


class AbstractAccountRepository(metaclass=ABCMeta):
    """
    Репозитория для счетов пользователей.
    """

    @abstractmethod
    def is_payment_entry_exists_by_transaction_id(
        self, transaction_id: TransactionId
    ) -> bool:
        """Существует ли платеж с указанным transaction_id?"""
        raise NotImplementedError

    @abstractmethod
    def is_user_has_account(self, user_id: UserId, account_id: AccountId) -> bool:
        """
        Есть ли счет у пользователя?
        """
        raise NotImplementedError

    @abstractmethod
    def save_account(self, account: Account) -> AccountId:
        """
        Сохранить счет.
        """
        raise NotImplementedError

    @abstractmethod
    def is_account_exists(self, account_id: AccountId) -> bool:
        """
        Существует ли счет?
        """
        raise NotImplementedError

    @abstractmethod
    def get_account_by_id(self, account_id: AccountId) -> Account:
        """
        Получить счет по id.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_accounts(self, user_id: UserId) -> list[Account]:
        """Получить список счетов пользователя."""
        raise NotImplementedError

    @abstractmethod
    def get_user_payments(self, user_id: UserId) -> list[PaymentEntry]:
        """Получить список платежей пользователя."""
        raise NotImplementedError


class FakeAccountRepository(AbstractAccountRepository):
    """Подставной репозиторий счетов пользователей для тестов."""

    def __init__(
        self,
        storage: dict[AccountId, Account] | None = None,
        account_serial: AccountId = AccountId(0),
    ) -> None:

        if storage is None:
            storage = {}

        self.storage: dict[AccountId, Account] = storage
        self.account_serial: int = account_serial

    def is_payment_entry_exists_by_transaction_id(
        self, transaction_id: TransactionId
    ) -> bool:
        for account in self.storage.values():
            for entry in account.payments:
                if entry.transaction_id == transaction_id:
                    return True

        return False

    def is_user_has_account(self, user_id: UserId, account_id: AccountId):
        for account in self.storage.values():
            if account.id_ == account_id and account.user_id == user_id:
                return True

        return False

    def save_account(self, account: Account) -> AccountId:
        if account.id_ is None:
            self.account_serial += 1
            account.id_ = AccountId(self.account_serial)
            for entry in account.payments:
                entry.account_id = account.id_
        elif not self.is_account_exists(account.id_):
            self.account_serial = account.id_ + 1

        self.storage[account.id_] = account

        return account.id_

    def is_account_exists(self, account_id: AccountId) -> bool:
        return account_id in self.storage

    def get_account_by_id(self, account_id: AccountId) -> Account:
        if not self.is_account_exists(account_id):
            raise ValueError("Указанный счет не существует")

        return self.storage[account_id]

    def get_user_accounts(self, user_id: UserId) -> list[Account]:
        user_accounts = []

        for account in self.storage.values():
            if account.user_id == user_id:
                user_accounts.append(account)

        return user_accounts

    def get_user_payments(self, user_id: UserId) -> list[PaymentEntry]:
        user_accounts = self.get_user_accounts(user_id)
        user_payments = []

        for account in user_accounts:
            user_payments.extend(account.payments)

        return user_payments


class SQLAlchemyAccountRepository(AbstractAccountRepository):
    """
    Репозиторий счетов для SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def is_payment_entry_exists_by_transaction_id(
        self, transaction_id: TransactionId
    ) -> bool:
        """Проверяет существование транзакции в таблице платежей."""
        stmt = select(
            exists().where(SQLAlchemyPaymentEntry.transaction_id == transaction_id)
        )
        return self._session.scalar(stmt) or False

    def is_user_has_account(self, user_id: UserId, account_id: AccountId) -> bool:
        """Проверяет принадлежность счета пользователю."""
        stmt = select(
            exists().where(
                SQLAlchemyAccount.id == account_id, SQLAlchemyAccount.user_id == user_id
            )
        )
        return self._session.scalar(stmt) or False

    def save_account(self, account: Account) -> AccountId:
        orm_account = AccountMapper.to_orm(account)
        is_new_account = orm_account.id is None

        if not is_new_account:
            # Обновляем существующую запись
            orm_account = self._session.merge(orm_account)
        else:
            # Добавляем новую запись
            self._session.add(orm_account)

        # Синхронизируем с БД, чтобы получить сгенерированный ID (если это был INSERT)
        self._session.flush()

        # Теперь id гарантированно существует
        account_id = AccountId(orm_account.id)

        # Если аккаунт был новый, обновляем доменную модель и её связи
        if is_new_account:
            account.id_ = account_id
            for payment in account.payments:
                payment.account_id = account_id

        return account_id

    def is_account_exists(self, account_id: AccountId) -> bool:
        stmt = select(exists().where(SQLAlchemyAccount.id == account_id))
        return self._session.scalar(stmt) or False

    def get_account_by_id(self, account_id: AccountId) -> Account:
        orm_account = self._session.get(SQLAlchemyAccount, account_id)

        if orm_account is None:
            raise ValueError(f"Счет с ID {account_id} не найден")

        return AccountMapper.to_domain(orm_account)

    def get_user_accounts(self, user_id: UserId) -> list[Account]:
        stmt = select(SQLAlchemyAccount).where(SQLAlchemyAccount.user_id == user_id)

        orm_accounts = self._session.scalars(stmt).all()
        accounts = [
            AccountMapper.to_domain(orm_account) for orm_account in orm_accounts
        ]

        return accounts

    def get_user_payments(self, user_id: UserId) -> list[PaymentEntry]:
        stmt = (
            select(SQLAlchemyPaymentEntry)
            .join(SQLAlchemyAccount)
            .where(SQLAlchemyAccount.user_id == user_id)
        )

        orm_payments = self._session.scalars(stmt).all()
        payments = [
            PaymentEntryMapper.to_domain(orm_payment) for orm_payment in orm_payments
        ]

        return payments


class AbstractUserRepository(metaclass=ABCMeta):
    @abstractmethod
    def is_user_exists(self, user_id: UserId) -> bool:
        """Существует ли пользователь?"""
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_id: UserId) -> UserDTO:
        """Получить пользователя."""
        raise NotImplementedError

    @abstractmethod
    def save_user(self, user: UserDTO) -> UserId:
        """Сохранить пользователя"""
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, user_id: UserId) -> None:
        """Удалить пользователя"""
        raise NotImplementedError

    @abstractmethod
    def get_users(self) -> list[UserDTO]:
        """Получить список пользователей"""
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email: str) -> UserDTO:
        raise NotImplementedError


class FakeUserRepository(AbstractUserRepository):
    """Подставной репозиторий со пользователями."""

    def __init__(
        self, storage: dict[UserId, UserDTO] | None = None, user_serial: int = 0
    ) -> None:
        if storage is None:
            storage = {}

        self.user_serial = user_serial
        self.storage = storage

    def is_user_exists(self, user_id: UserId) -> bool:
        for user in self.storage.values():
            if user.user_id == user_id:
                return True

        return False

    def get_user(self, user_id: UserId) -> UserDTO:
        if not self.is_user_exists(user_id):
            raise ValueError("Указанный пользователь не существует")

        user = self.storage[user_id]
        return user

    def save_user(self, user: UserDTO) -> UserId:
        if user.user_id is None:
            self.user_serial += 1
            user.user_id = UserId(self.user_serial)

        elif user.user_id not in self.storage:
            if isinstance(user.user_id, int) and user.user_id > self.user_serial:
                self.user_serial = user.user_id

        self.storage[user.user_id] = user

        return user.user_id

    def delete_user(self, user_id: UserId) -> None:
        if not self.is_user_exists(user_id):
            raise ValueError("Указанный пользователь не существует")

        self.storage.pop(user_id)

    def get_users(self) -> list[UserDTO]:
        users = list(self.storage.values())
        return users

    def get_user_by_email(self, email: str) -> UserDTO:
        for user in self.storage.values():
            if user.email == email:
                return user

        raise UserDoesNotExists
