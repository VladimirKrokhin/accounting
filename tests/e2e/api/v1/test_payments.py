import pytest
import hashlib
from uuid import uuid4
from accounts.adapters.sqlalchemy.models import Base
from accounts.entrypoints.sanic_app import create_app, init_app
from accounts.entrypoints.sanic_app.status_codes import StatusCodes
from accounts.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from e2e.api.v1.api_client import post_transaction


@pytest.fixture
async def signature_test_app():
    app = create_app()
    await init_app(app)

    uow: SqlAlchemyUnitOfWork = app.ctx.uow
    app.config.PAYMENT_SYSTEM_SECRET_KEY = "gfdmhghif38yrf9ew0jkf32"

    async with uow:
        session = uow.session
        engine = session.bind

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    yield app


@pytest.mark.asyncio
async def test_webhook_transaction_success(test_client, regular_user, test_app):
    # 1. Подготовка данных
    secret = test_app.config.PAYMENT_SYSTEM_SECRET_KEY
    assert secret == "gfdmhghif38yrf9ew0jkf32"

    t_id = "5eae174f-7cd0-472c-bd36-35660f00132b"
    user_id = 1
    account_id = 1  # Предполагаем, что счет 1 существует
    amount = 100

    signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"

    # 3. Отправка вебхука
    request, response = await post_transaction(
        test_client,
        transaction_id=t_id,
        account_id=account_id,
        user_id=user_id,
        amount=amount,
        signature=signature,
    )

    assert response.status_code == StatusCodes.SUCCESS_CREATED
    assert response.json["status"] == "success"


@pytest.mark.asyncio
async def test_webhook_invalid_signature(test_client, regular_user):
    request, response = await post_transaction(
        test_client,
        transaction_id=str(uuid4()),
        account_id=1,
        user_id=regular_user.user_id,
        amount=100,
        signature="fake_signature_123",
    )

    assert response.status_code == StatusCodes.ERROR_UNPROCESSABLE_ENTITY
    assert response.json["message"] == "signature is not valid"
