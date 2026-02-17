from sanic import Blueprint

from accounts.entrypoints.sanic_app.api.v1.routes import get_api_v1_bp

__all__ = ["get_api_bp"]


def get_api_bp():
    api_v1 = get_api_v1_bp()

    api = Blueprint.group(api_v1, url_prefix="/api")
    return api
