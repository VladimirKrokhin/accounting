from sanic import Blueprint
from entrypoints.sanic_app.routes.v1 import api_v1


__all__ = ["api"]

api = Blueprint.group(api_v1, url_prefix="/api")
