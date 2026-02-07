from abc import ABCMeta, abstractmethod

from sqlalchemy import exists, select
from sqlalchemy.orm import Session
from domain.models import Account, AccountId, UserId, TransactionId
from adapters.sqlalchemy.mappers import (
    AccountMapper,
    SQLAlchemyAccount,
    SQLAlchemyPaymentEntry,
)


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

        # Если аккаунт уже существует в базе
        if orm_account.id is not None:
            merged = self._session.merge(orm_account)
        else:
            self._session.add(orm_account)
            merged = orm_account

        self._session.flush()
        return AccountId(merged.id)

    def is_account_exists(self, account_id: AccountId) -> bool:
        if account_id is None:
            return False
        stmt = select(exists().where(SQLAlchemyAccount.id == account_id))
        return self._session.scalar(stmt) or False

    def get_account_by_id(self, account_id: AccountId) -> Account:
        # Мы используем get(), так как это наиболее эффективный способ поиска по PK
        orm_account = self._session.get(SQLAlchemyAccount, account_id)

        if orm_account is None:
            raise ValueError(f"Счет с ID {account_id} не найден")

        return AccountMapper.to_domain(orm_account)
