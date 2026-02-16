from __future__ import annotations
import abc
from sqlalchemy.orm import sessionmaker

from accounts.adapters.repository import (
    AbstractAccountRepository,
    AbstractUserRepository,
    FakeAccountRepository,
    FakeUserRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyUserRepository,
)

__all__ = ["AbstractUnitOfWork", "FakeUnitOfWork", "SqlAlchemyUnitOfWork"]


class AbstractUnitOfWork(abc.ABC):
    accounts: AbstractAccountRepository
    users: AbstractUserRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        accounts: FakeAccountRepository | None = None,
        users: FakeUserRepository | None = None,
    ):
        if accounts is None:
            accounts = FakeAccountRepository()

        if users is None:
            users = FakeUserRepository()

        self.accounts = accounts
        self.users = users
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.accounts = SQLAlchemyAccountRepository(self.session)
        self.users = SQLAlchemyUserRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
