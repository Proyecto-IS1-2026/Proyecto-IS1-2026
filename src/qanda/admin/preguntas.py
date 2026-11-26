
from flask import (
    abort,
    current_app,
    flash,
    redirect,
    url_for,
)
from flask_login import current_user

from qanda.admin import admin_bp
from qanda.admin.servicios import (
    eliminar_pregunta as eliminar_pregunta_servicio,
)
from qanda.auth.decorators import admin_required
from qanda.models import Pregunta


@admin_bp.route(
    "/preguntas/<uuid:pregunta_id>/eliminar",
    methods=["POST"]
)
@admin_required
def eliminar_pregunta(pregunta_id):

    session_factory = current_app.extensions["db_session_factory"]

    with session_factory.begin() as session:

        pregunta = session.get(Pregunta, pregunta_id)

        if pregunta is None:
            abort(404)

        eliminar_pregunta_servicio(
            session,
            pregunta,
            current_user._get_current_object(),
        )

    flash(
        "La pregunta fue eliminada correctamente.",
        "success"
    )

    return redirect(url_for("admin.moderacion"))
