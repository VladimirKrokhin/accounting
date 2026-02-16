import os
import pytest
from sanic import Sanic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import retry, stop_after_delay
from sanic_testing import TestManager

from accounts.adapters.sqlalchemy.models import Base
from accounts.bootstrap import bootstrap
from accounts.service_layer.unit_of_work import (
    FakeUnitOfWork,
    SqlAlchemyUnitOfWork,
)


def get_postgres_uri():
    """
    Формирует строку подключения к Postgres из переменных окружения.
    Значения по умолчанию соответствуют стандартным настройкам или локальному Docker.
    """
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db_name = os.environ.get("POSTGRES_DB_NAME", "postgres")

    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


@pytest.fixture(scope="session")
def postgres_db():
    # 1. Либо импортируйте конфиг напрямую, либо используйте env-переменные
    # Не используйте sanic_app здесь, чтобы не было цикла

    engine = create_engine(get_postgres_uri(), isolation_level="SERIALIZABLE")

    @retry(stop=stop_after_delay(10))
    def wait_for_db():
        with engine.connect() as conn:
            return conn

    wait_for_db()
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def sanic_app(postgres_db):
    from accounts.entrypoints.sanic_app import app, init_app

    session_factory = sessionmaker(bind=postgres_db)
    test_uow = SqlAlchemyUnitOfWork(session_factory)
    # test_uow = FakeUnitOfWork()
    message_bus = bootstrap(test_uow)

    init_app(app, message_bus=message_bus)

    return app


@pytest.fixture
def test_client(sanic_app):
    mgr = TestManager(sanic_app)
    return mgr.test_client


@pytest.fixture(autouse=True)
def clean_db(postgres_db):
    """Очистка таблиц перед каждым тестом"""
    yield
    for table in reversed(Base.metadata.sorted_tables):
        with postgres_db.connect() as conn:
            conn.execute(table.delete())
            conn.commit()
