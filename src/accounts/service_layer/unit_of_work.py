import abc
import os
from sqlalchemy import create_engine
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


def get_postgres_uri():
    """
    Формирует строку подключения к Postgres из переменных окружения.
    Значения по умолчанию соответствуют стандартным настройкам или локальному Docker.
    """
    user = os.environ.get("POSTGRES_USER", "accounts")
    password = os.environ.get("POSTGRES_PASSWORD", "accounts")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db_name = os.environ.get("POSTGRES_DB_NAME", "accounts")

    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


DEFAULT_SQLALCHEMY_ENGINE = create_engine(
    get_postgres_uri(),
    isolation_level="REPEATABLE READ",
)


DEFAULT_SESSION_FACTORY = sessionmaker(bind=DEFAULT_SQLALCHEMY_ENGINE)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.accounts = SQLAlchemyAccountRepository(self.session)
        self.users = SQLAlchemyUserRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            pass

        self.session.close()
        del self.session

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
