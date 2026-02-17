# import pytest
# from accounts.entrypoints.sanic_app.status_codes import StatusCodes
# from e2e.api.v1.api_client import post_auth
#
#
# def test_login_fail_user_not_found(test_client):
#     status, body = post_auth(test_client, "ghost@example.com", "123456")
#
#     assert status == StatusCodes.ERROR_UNAUTHORIZED
