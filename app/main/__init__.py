from flask import Blueprint

bp = Blueprint("main", __name__)

from app.main import privacy, routes, seo  # noqa: E402,F401
