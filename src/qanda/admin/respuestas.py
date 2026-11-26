
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
    eliminar_respuesta as eliminar_respuesta_servicio,
)
from qanda.auth.decorators import admin_required
from qanda.models import Respuesta


@admin_bp.route(
    "/respuestas/<uuid:respuesta_id>/eliminar",
    methods=["POST"]
)
@admin_required
def eliminar_respuesta(respuesta_id):

    session_factory = current_app.extensions["db_session_factory"]

    with session_factory.begin() as session:

        respuesta = session.get(Respuesta, respuesta_id)

        if respuesta is None:
            abort(404)

        eliminar_respuesta_servicio(
            session,
            respuesta,
            current_user._get_current_object(),
        )

    flash(
        "La respuesta fue eliminada correctamente.",
        "success"
    )

    return redirect(url_for("admin.moderacion"))
