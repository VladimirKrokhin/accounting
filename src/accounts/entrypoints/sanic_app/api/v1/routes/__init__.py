from sanic import Blueprint

from accounts.entrypoints.sanic_app.api.v1.middlewares.auth import protected
from accounts.entrypoints.sanic_app.api.v1.routes.auth import auth_bp
from accounts.entrypoints.sanic_app.api.v1.routes.payments import payment_bp
from accounts.entrypoints.sanic_app.api.v1.routes.users import users_api

__all__ = ["api_v1"]


api_v1 = Blueprint.group(auth_bp, payment_bp, users_api, url_prefix="/v1")
