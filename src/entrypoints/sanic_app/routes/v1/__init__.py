from sanic import Blueprint
from entrypoints.sanic_app.routes.v1.auth import auth_bp
from entrypoints.sanic_app.routes.v1.payments import payment_bp
from entrypoints.sanic_app.routes.v1.user import user_bp


__all__ = ["api_v1"]

api_v1 = Blueprint.group(auth_bp, payment_bp, user_bp, url_prefix="/v1")
