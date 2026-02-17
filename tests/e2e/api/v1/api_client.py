from sanic.models.handler_types import Sanic
from sanic_testing.testing import SanicASGITestClient

API_URI = "/api/v1"


async def post_auth(test_client: SanicASGITestClient, email: str, password: str):
    auth_uri = API_URI + "/auth"

    request, response = await test_client.post(
        auth_uri,
        json={
            "email": email,
            "password": password,
        },
    )

    return request, response


async def post_transaction(
    test_client: SanicASGITestClient,
    transaction_id: str,
    account_id: int,
    user_id: int,
    amount: float,
    signature: str,
):
    transactions_url = API_URI + "/transactions"

    request, response = await test_client.post(
        transactions_url,
        json={
            "transaction_id": transaction_id,
            "user_id": user_id,
            "account_id": account_id,
            "amount": amount,
            "signature": signature,
        },
    )

    return request, response


USERS_URI = API_URI + "/users"
ME_URI = USERS_URI + "/me"


async def get_current_user(test_client: SanicASGITestClient, token: str):
    me_uri = ME_URI

    request, response = await test_client.get(
        me_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    return request, response


async def get_current_user_accounts(test_client: SanicASGITestClient, token: str):
    me_accounts_uri = ME_URI + "/accounts"

    request, response = await test_client.get(
        me_accounts_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    return request, response


async def get_current_user_payments(test_client: SanicASGITestClient, token: str):
    me_payments_uri = ME_URI + "/payments"

    request, response = await test_client.get(
        me_payments_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    return request, response


async def post_create_user(
    test_client: SanicASGITestClient,
    token: str,
    email: str,
    full_name: str,
    password: str,
):
    user_uri = USERS_URI

    request, response = await test_client.post(
        user_uri,
        json=dict(
            email=email,
            full_name=full_name,
            password=password,
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

    return request, response


async def delete_user(test_client: SanicASGITestClient, token: str, user_id: int):
    delete_user_uri = USERS_URI + f"/{user_id}"

    request, response = await test_client.delete(
        delete_user_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    return request, response


async def put_user(
    test_client: SanicASGITestClient,
    token: str,
    email: str,
    full_name: str,
    password: str,
    user_id: int,
):
    patch_user_uri = USERS_URI + f"/{user_id}"

    request, response = await test_client.put(
        patch_user_uri,
        json=dict(
            email=email,
            full_name=full_name,
            password=password,
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

    return request, response


async def get_users(test_client: SanicASGITestClient, token: str):
    get_users_uri = USERS_URI + "/"

    request, response = await test_client.get(
        get_users_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    return request, response


async def get_user_accounts(test_client: SanicASGITestClient, token: str, user_id: int):
    get_user_accounts_uri = USERS_URI + f"/{user_id}/accounts"

    request, response = await test_client.get(
        get_user_accounts_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    return request, response
