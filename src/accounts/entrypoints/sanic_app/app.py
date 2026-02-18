from sanic import Sanic

from accounts.adapters.sqlalchemy.db import (
    init_db,
)
from accounts.config import PostgresConfig, load_config
from accounts.service_layer.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from accounts.entrypoints.sanic_app.api import get_api_bp

__all__ = ["create_app", "init_app"]


def create_app() -> Sanic:
    app = Sanic("accounts")

    api = get_api_bp()
    app.blueprint(api)

    @app.before_server_start
    async def bootstrap_app(app: Sanic):
        await init_app(app)

    return app


async def init_uow(postgres_config: PostgresConfig):
    session_factory = await init_db(postgres_config)
    uow = SqlAlchemyUnitOfWork(session_factory)

    return uow


async def init_app(app: Sanic, config=None) -> Sanic:
    app_config = config or load_config()

    app.update_config(app_config)
    uow = await init_uow(app_config.get_postgres_config())
    app.ctx.uow = uow

    return app
