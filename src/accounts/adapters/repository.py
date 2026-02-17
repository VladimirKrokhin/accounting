from abc import ABCMeta, abstractmethod
from typing import Sequence

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from accounts.dtos import UserDTO
from accounts.core.types import AccountId, UserId, TransactionId
from accounts.core.entities import Account, PaymentEntry
from accounts.core.exceptions import AccountDoesNotExists, UserDoesNotExists

from accounts.adapters.sqlalchemy.models import User
from accounts.adapters.sqlalchemy.mappers import (
    AccountMapper,
    PaymentEntryMapper,
    SQLAlchemyAccount,
    SQLAlchemyPaymentEntry,
    UserMapper,
)

__all__ = [
    "AbstractAccountRepository",
    "SQLAlchemyAccountRepository",
    "AbstractUserRepository",
    "SQLAlchemyUserRepository",
]


class AbstractAccountRepository(metaclass=ABCMeta):
    """
    Abstract Repository for User's accounts
    """

    @abstractmethod
    async def does_payment_entry_exist_by_transaction_id(
        self, transaction_id: TransactionId
    ) -> bool:
        """Does a PaymentEntry exists with specified transaction_id?
        :param transaction_id: Entry's transaction id
        :type transaction_id: TransactionId

        :return: True, if exists, else False
        :rtype: bool
        """

        raise NotImplementedError

    @abstractmethod
    async def does_user_have_account(
        self, user_id: UserId, account_id: AccountId
    ) -> bool:
        """Does an User have an Account?
        :param user_id: User's ID
        :type user_id: UserId
        :param account_id: Account's ID
        :type account_id: AccountId

        :return: True if has else False
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    async def save_account(self, account: Account) -> AccountId:
        """Save account.
        :param account: Account to save
        :type account: Account

        :return: Account's ID
        :rtype: AccountId
        """
        raise NotImplementedError

    @abstractmethod
    async def does_account_exist(self, account_id: AccountId) -> bool:
        """Does Account exists?
        :param account_id: Account's ID
        :type account_id: AccountId

        :return: True if exists else False
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    async def get_account_by_id(self, account_id: AccountId) -> Account:
        """Get Account by ID.
        :param account_id: Account's ID
        :type account_id: AccountId

        :raises AccountDoesNotExists: if Account with specific ID does not exists

        :return: Account, if exists
        :rtype: Account
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user_accounts(self, user_id: UserId) -> list[Account]:
        """Get User's accounts list.
        :param user_id: User's ID
        :type user_id: UserId

        :return: list of Accounts, owned by User
        :rtype: list[Account]"""
        raise NotImplementedError

    @abstractmethod
    async def get_user_payments(self, user_id: UserId) -> list[PaymentEntry]:
        """Get User's payments list.
        :param user_id: User's ID
        :type user_id: UserId

        :return: User's PaymentEntries list
        :rtype: list[PaymentEntry]
        """
        raise NotImplementedError


class SQLAlchemyAccountRepository(AbstractAccountRepository):
    """
    SQLAlchemy Account Repository.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def does_payment_entry_exist_by_transaction_id(
        self, transaction_id: TransactionId
    ) -> bool:
        stmt = select(
            exists().where(SQLAlchemyPaymentEntry.transaction_id == transaction_id)
        )
        return await self._session.scalar(stmt) or False

    async def does_user_have_account(
        self, user_id: UserId, account_id: AccountId
    ) -> bool:
        stmt = select(
            exists().where(
                SQLAlchemyAccount.id == account_id, SQLAlchemyAccount.user_id == user_id
            )
        )
        return await self._session.scalar(stmt) or False

    async def save_account(self, account: Account) -> AccountId:
        orm_account = AccountMapper.to_orm(account)
        is_new_account = orm_account.id is None

        if not is_new_account:
            orm_account = await self._session.merge(orm_account)
        else:
            self._session.add(orm_account)

        await self._session.flush()

        account_id = AccountId(orm_account.id)

        if is_new_account:
            account.id_ = account_id
            for payment in account.payments:
                payment.account_id = account_id

        return account_id

    async def does_account_exist(self, account_id: AccountId) -> bool:
        stmt = select(exists().where(SQLAlchemyAccount.id == account_id))
        return await self._session.scalar(stmt) or False

    async def get_account_by_id(self, account_id: AccountId) -> Account:
        orm_account: SQLAlchemyAccount | None = await self._session.get(
            SQLAlchemyAccount,
            account_id,
            options=[selectinload(SQLAlchemyAccount.payments)],
        )

        if orm_account is None:
            raise AccountDoesNotExists(f"Account with id={account_id} does not exists")

        return AccountMapper.to_domain(orm_account)

    async def get_user_accounts(self, user_id: UserId) -> list[Account]:
        stmt = (
            select(SQLAlchemyAccount)
            .where(SQLAlchemyAccount.user_id == user_id)
            .options(selectinload(SQLAlchemyAccount.payments))
        )

        orm_accounts: Sequence[SQLAlchemyAccount] = (
            await self._session.scalars(stmt)
        ).all()

        accounts = [
            AccountMapper.to_domain(orm_account) for orm_account in orm_accounts
        ]

        return accounts

    async def get_user_payments(self, user_id: UserId) -> list[PaymentEntry]:
        stmt = (
            select(SQLAlchemyPaymentEntry)
            .join(SQLAlchemyAccount)
            .where(SQLAlchemyAccount.user_id == user_id)
        )

        orm_payments: Sequence[SQLAlchemyPaymentEntry] = (
            await self._session.scalars(stmt)
        ).all()
        payments = [
            PaymentEntryMapper.to_domain(orm_payment) for orm_payment in orm_payments
        ]

        return payments


class AbstractUserRepository(metaclass=ABCMeta):
    """Abstract User Repository."""

    @abstractmethod
    async def does_user_exist(self, user_id: UserId) -> bool:
        """Существует ли пользователь?"""
        raise NotImplementedError

    @abstractmethod
    async def does_user_exist_by_email(self, email: str) -> bool:
        """Существует ли пользователь с указанной почтой?"""
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: UserId) -> UserDTO:
        """Получить пользователя.

        :raises UserDoesNotExists: if User with specified user_id does not exist
        """
        raise NotImplementedError

    @abstractmethod
    async def save_user(self, user: UserDTO) -> UserId:
        """Сохранить пользователя"""
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: UserId) -> None:
        """Удалить пользователя"""
        raise NotImplementedError

    @abstractmethod
    async def get_users(self) -> list[UserDTO]:
        """Получить список пользователей"""
        raise NotImplementedError

    @abstractmethod
    async def get_users_by_email(self, email: str) -> list[UserDTO]:
        raise NotImplementedError


class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def does_user_exist(self, user_id: UserId) -> bool:
        stmt = select(exists().where(User.id == user_id))
        return await self._session.scalar(stmt) or False

    async def does_user_exist_by_email(self, email: str) -> bool:
        stmt = select(exists().where(User.email_address == email))
        return await self._session.scalar(stmt) or False

    async def get_user(self, user_id: UserId) -> UserDTO:
        orm_user: User | None = await self._session.get(User, user_id)

        if not orm_user:
            raise UserDoesNotExists(f"Cannot get User {user_id}: not found")

        return UserMapper.to_dto(orm_user)

    async def save_user(self, user_dto: UserDTO) -> UserId:
        orm_user = UserMapper.to_orm(user_dto)

        if orm_user.id is not None:
            # Обновление существующего (включая все связанные таблицы наследования)
            orm_user = await self._session.merge(orm_user)
        else:
            # Создание нового
            self._session.add(orm_user)

        await self._session.flush()  # Получаем ID из БД

        new_id = UserId(orm_user.id)
        user_dto.user_id = new_id
        return new_id

    async def delete_user(self, user_id: UserId) -> None:
        user = await self._session.get(User, user_id)
        if not user:
            raise UserDoesNotExists(f"User with id {user_id} not found")

        await self._session.delete(user)
        await self._session.flush()

    async def get_users(self) -> list[UserDTO]:
        stmt = select(User)
        users: Sequence[User] = (await self._session.scalars(stmt)).all()
        return [UserMapper.to_dto(u) for u in users]

    async def get_users_by_email(self, email: str) -> list[UserDTO]:
        stmt = select(User).where(User.email_address == email)
        users: Sequence[User] = (await self._session.scalars(stmt)).all()
        return [UserMapper.to_dto(u) for u in users]
