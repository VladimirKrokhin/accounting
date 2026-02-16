from sanic import Sanic

from accounts.adapters.sqlalchemy.models import Base
from accounts.config import load_config
from accounts.dtos import UserDTO, UserType
from accounts.core.entities import UserId
from accounts.adapters.repository import FakeAccountRepository, FakeUserRepository
from accounts.service_layer.unit_of_work import (
    DEFAULT_SQLALCHEMY_ENGINE,
    FakeUnitOfWork,
    SqlAlchemyUnitOfWork,
)
from accounts.entrypoints.sanic_app.api import api

__all__ = ["app", "init_app"]

app = Sanic("accounts")
app.blueprint(api)


@app.before_server_start
async def bootstrap_app(app: Sanic):
    init_app(app)


def init_app(app: Sanic, uow=None) -> Sanic:
    app_config = load_config()
    app.update_config(app_config)

    Base.metadata.create_all(DEFAULT_SQLALCHEMY_ENGINE)

    if uow is not None:
        app.ctx.uow = uow
    elif not hasattr(app.ctx, "uow"):
        uow = SqlAlchemyUnitOfWork()

        # account_repository = FakeAccountRepository()
        #
        # test_user = UserDTO(
        #     user_id=UserId(1),
        #     email="test@user.example",
        #     password_hash="$2b$12$7T/BsPgD4IrwlvYFEQb6Wug27mxMQ2tBKEiTQpwVk8i6YJQvKCMly",  # test_user
        #     full_name="Test User",
        #     user_type=UserType.USER,
        # )
        #
        # test_admin = UserDTO(
        #     user_id=UserId(2),
        #     email="test@admin.example",
        #     password_hash="$2b$12$HQD9l658BQ4EmJRIMyw4DOoIWWfvvi3JrZy0CDFH49pgGWu4wrHPK",  # test_admin
        #     full_name="Test Admin",
        #     user_type=UserType.ADMIN,
        # )
        #
        # users: dict[UserId, UserDTO] = {
        #     test_user.user_id: test_user,
        #     test_admin.user_id: test_admin,
        # }  # pyright: ignore[reportAssignmentType]
        #
        # user_repository = FakeUserRepository(users, user_serial=2)
        # uow = FakeUnitOfWork(accounts=account_repository, users=user_repository)
        app.ctx.uow = uow

    return app
