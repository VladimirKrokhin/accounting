from sanic import Sanic
from domain.models import UserId
from dtos import UserDTO, UserType
from entrypoints.sanic_app.api import api
from bootstrap import bootstrap
from adapters.repository import FakeAccountRepository, FakeUserRepository

app = Sanic("accounts")
app.blueprint(api)


@app.before_server_start
async def attach_dependencies(app):
    # FIXME: замени на использование конфига
    # TODO: Создай метод для загрузки конфига
    secret_key = "gfdmhghif38yrf9ew0jkf32"
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

    users = {
        test_user.user_id: test_user,
        test_admin.user_id: test_admin,
    }
    user_repository = FakeUserRepository(users, user_serial=2)

    handlers = bootstrap(
        account_repository=account_repository,
        user_repository=user_repository,
        secret=secret_key,
    )
    app.ctx.handlers = handlers
    app.ctx.account_repository = account_repository
    app.ctx.user_repository = user_repository
