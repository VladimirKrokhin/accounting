from sanic import Blueprint

from accounts.entrypoints.sanic_app.api.v1.routes.auth import get_auth_bp
from accounts.entrypoints.sanic_app.api.v1.routes.payments import (
    get_payment_bp,
)
from accounts.entrypoints.sanic_app.api.v1.routes.users import get_users_bp

__all__ = ["get_api_v1_bp"]


def get_api_v1_bp():
    auth_bp = get_auth_bp()
    payment_bp = get_payment_bp()
    users_bp = get_users_bp()

    api_v1 = Blueprint.group(auth_bp, payment_bp, users_bp, url_prefix="/v1")

    return api_v1
