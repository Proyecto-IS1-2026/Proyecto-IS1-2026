from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

from qanda.auth import routes  # noqa: F401