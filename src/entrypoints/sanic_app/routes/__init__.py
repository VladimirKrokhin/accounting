from sanic import Blueprint
from entrypoints.sanic_app.routes.admin import admin_bp
from entrypoints.sanic_app.routes.auth import auth_bp
from entrypoints.sanic_app.routes.payments import payment_bp
from entrypoints.sanic_app.routes.user import user_bp


__all__ = ["api"]

api = Blueprint.group(admin_bp, auth_bp, payment_bp, user_bp, url_prefix="/api")
