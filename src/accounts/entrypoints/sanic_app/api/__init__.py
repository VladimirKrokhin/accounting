from sanic import Blueprint

from accounts.entrypoints.sanic_app.api.v1.routes import api_v1

__all__ = ["api"]

api = Blueprint.group(api_v1, url_prefix="/api")
