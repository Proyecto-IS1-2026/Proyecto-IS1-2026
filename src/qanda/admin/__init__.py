
from flask import Blueprint

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

from qanda.admin import routes  # noqa: F401
from qanda.admin import preguntas  # noqa: F401
from qanda.admin import respuestas  # noqa: F401
