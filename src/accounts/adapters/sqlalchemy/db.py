from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from accounts.adapters.sqlalchemy.models import Base
from accounts.config import PostgresConfig


def get_postgres_uri(config: PostgresConfig):
    user = config.user
    password = config.password
    host = config.host
    port = config.port
    db_name = config.db_name

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"


def create_async_sqlalchemy_engine(config: PostgresConfig):
    return create_async_engine(
        get_postgres_uri(config),
        isolation_level="REPEATABLE READ",
    )


def create_async_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db(config: PostgresConfig) -> async_sessionmaker:
    engine = create_async_sqlalchemy_engine(config)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = create_async_session_factory(engine)

    return session_factory
