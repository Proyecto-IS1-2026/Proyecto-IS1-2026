
from flask import Blueprint

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

from qanda.admin import (
    preguntas,  # noqa: F401
    respuestas,  # noqa: F401
    routes,  # noqa: F401
)
