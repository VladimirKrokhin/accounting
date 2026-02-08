from sanic import Sanic
from entrypoints.sanic_app.routes import api
from bootstrap import bootstrap
from adapters.repository import FakeAccountRepository

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

    handlers = bootstrap(
        account_repository=account_repository,
        secret=secret_key,
    )
    app.ctx.handlers = handlers
    app.ctx.account_repository = account_repository
