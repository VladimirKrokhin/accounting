from sanic import Sanic
from domain.models import UserId
from dtos import UserDTO, UserType
from entrypoints.sanic_app.routes import api
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

    user_id = UserId(1)
    users = {
        user_id: UserDTO(
            user_id=user_id,
            email="test@user.example",
            full_name="Test User",
            user_type=UserType.USER,
        )
    }
    user_repository = FakeUserRepository(users)

    handlers = bootstrap(
        account_repository=account_repository,
        user_repository=user_repository,
        secret=secret_key,
    )
    app.ctx.handlers = handlers
    app.ctx.account_repository = account_repository
    app.ctx.user_repository = user_repository
