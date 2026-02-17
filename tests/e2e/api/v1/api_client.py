from sanic_testing.manager import SanicTestClient

API_URI = "/api/v1"


def post_auth(sanic_test_client: SanicTestClient, email: str, password: str):
    auth_uri = API_URI + "/auth"

    request, response = sanic_test_client.post(
        auth_uri,
        json={
            "email": email,
            "password": password,
        },
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


def post_transaction(
    sanic_test_client: SanicTestClient,
    transaction_id: str,
    account_id: int,
    user_id: int,
    amount: float,
    signature: str,
):
    transactions_url = API_URI + "/transactions"

    request, response = sanic_test_client.post(
        transactions_url,
        json={
            "transaction_id": transaction_id,
            "user_id": user_id,
            "account_id": account_id,
            "amount": amount,
            "signature": signature,
        },
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


USERS_URI = API_URI + "/users"
ME_URI = USERS_URI + "/me"


def get_current_user(sanic_test_client: SanicTestClient, token: str):
    me_uri = ME_URI

    request, response = sanic_test_client.get(
        me_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


def get_current_user_accounts(sanic_test_client: SanicTestClient, token: str):
    me_accounts_uri = ME_URI + "/accounts"

    request, response = sanic_test_client.get(
        me_accounts_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


def get_current_user_payments(sanic_test_client: SanicTestClient, token: str):
    me_payments_uri = ME_URI + "/payments"

    request, response = sanic_test_client.get(
        me_payments_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


def post_create_user(
    sanic_test_client: SanicTestClient,
    token: str,
    email: str,
    full_name: str,
    password: str,
):
    user_uri = USERS_URI

    request, response = sanic_test_client.post(
        user_uri,
        json=dict(
            email=email,
            full_name=full_name,
            password=password,
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


def delete_user(sanic_test_client: SanicTestClient, token: str, user_id: int):
    delete_user_uri = USERS_URI + f"/{user_id}"

    request, response = sanic_test_client.delete(
        delete_user_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


def patch_user(
    sanic_test_client: SanicTestClient,
    token: str,
    email: str,
    full_name: str,
    password: str,
    user_id: int,
):
    patch_user_uri = USERS_URI + f"/{user_id}"

    request, response = sanic_test_client.patch(
        patch_user_uri,
        json=dict(
            email=email,
            full_name=full_name,
            password=password,
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


def get_users(sanic_test_client: SanicTestClient, token: str):
    get_users_uri = USERS_URI + "/"

    request, response = sanic_test_client.get(
        get_users_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    json = response.json
    status_code = response.status_code

    return status_code, json


def get_user_accounts(sanic_test_client: SanicTestClient, token: str, user_id: int):
    get_user_accounts_uri = USERS_URI + f"/{user_id}/accounts"

    request, response = sanic_test_client.get(
        get_user_accounts_uri,
        headers={"Authorization": f"Bearer {token}"},
    )

    json = response.json
    status_code = response.status_code

    return status_code, json
