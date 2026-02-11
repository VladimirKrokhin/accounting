from sanic import Sanic
from config import load_config

from bootstrap import bootstrap
from dtos import UserDTO, UserType
from domain.models import UserId
from adapters.repository import FakeAccountRepository, FakeUserRepository
from service_layer.unit_of_work import FakeUnitOfWork
from entrypoints.sanic_app.api import api

__all__ = ["app"]

app = Sanic("accounts")
app.blueprint(api)


@app.before_server_start
async def bootstrap_app(app: Sanic):
    init_app(app)


def init_app(app: Sanic, message_bus=None) -> Sanic:
    # FIXME: замени на использование конфига
    # TODO: Создай метод для загрузки конфига
    app_config = load_config()
    app.update_config(app_config)

    if message_bus is None:

        # FIXME: замени на SQLAlchemyRepository
        # TODO: создай метод инициализации приложения
        account_repository = FakeAccountRepository()

        test_user = UserDTO(
            user_id=UserId(1),
            email="test@user.example",
            password_hash="$2b$12$7T/BsPgD4IrwlvYFEQb6Wug27mxMQ2tBKEiTQpwVk8i6YJQvKCMly",  # test_user
            full_name="Test User",
            user_type=UserType.USER,
        )

        test_admin = UserDTO(
            user_id=UserId(2),
            email="test@admin.example",
            password_hash="$2b$12$HQD9l658BQ4EmJRIMyw4DOoIWWfvvi3JrZy0CDFH49pgGWu4wrHPK",  # test_admin
            full_name="Test Admin",
            user_type=UserType.ADMIN,
        )

        users: dict[UserId, UserDTO] = {
            test_user.user_id: test_user,
            test_admin.user_id: test_admin,
        }  # pyright: ignore[reportAssignmentType]

        user_repository = FakeUserRepository(users, user_serial=2)
        unit_of_work = FakeUnitOfWork(
            accounts=account_repository, users=user_repository
        )

        message_bus = bootstrap(unit_of_work)

    app.ctx.message_bus = message_bus
    return app
