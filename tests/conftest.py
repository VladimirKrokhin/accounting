from dotenv import find_dotenv, load_dotenv
import pytest
from sanic_testing import TestManager

from accounts.adapters.auth import generate_password_hash
from accounts.config import load_config
from accounts.core.types import UserId
from accounts.dtos import UserDTO, UserType
from accounts.entrypoints.sanic_app import create_app, init_app
from accounts.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from accounts.adapters.sqlalchemy.models import Base

test_dotenv = find_dotenv(".envs/.env.tests")
load_dotenv(test_dotenv, override=True)


@pytest.fixture
async def test_app():

    config = load_config()
    print(
        f"\n[TEST_DB_CHECK] Host: {config.POSTGRES_HOST}, DB: {config.POSTGRES_DB_NAME}"
    )
    app = create_app()

    await init_app(app, config)

    uow: SqlAlchemyUnitOfWork = app.ctx.uow

    async with uow:
        session = uow.session
        engine = session.bind

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    yield app


@pytest.fixture
def test_client(test_app):
    test_client = test_app.asgi_client
    return test_client


@pytest.fixture
async def admin_user(test_app):
    uow = test_app.ctx.uow

    user_id = UserId(1000)
    email = "test@admin.user"
    full_name = "Test Admin"
    user_type = UserType.ADMIN
    password_hash = generate_password_hash("admin_pass")

    admin_user = UserDTO(
        user_id=user_id,
        email=email,
        full_name=full_name,
        user_type=user_type,
        password_hash=password_hash,
    )

    async with uow:
        await uow.users.save_user(admin_user)
        await uow.commit()

    return admin_user


@pytest.fixture
async def regular_user(test_app):
    uow = test_app.ctx.uow

    user_id = UserId(1)
    email = "test@accounts.user"
    full_name = "Test User"
    user_type = UserType.USER
    password_hash = generate_password_hash("user_pass")

    regular_user = UserDTO(
        user_id=user_id,
        email=email,
        full_name=full_name,
        user_type=user_type,
        password_hash=password_hash,
    )

    async with uow:
        await uow.users.save_user(regular_user)
        await uow.commit()

    return regular_user
