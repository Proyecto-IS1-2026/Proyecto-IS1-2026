from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from qanda.admin import admin_bp
from qanda.admin.servicios import eliminar_pregunta as eliminar_pregunta_servicio
from qanda.auth.decorators import admin_required
from qanda.models import Pregunta, Usuario


@admin_bp.route("/usuarios", methods=["GET"])
@admin_required
def usuarios():
    session_factory = current_app.extensions["db_session_factory"]

    with session_factory() as session:
        usuarios = session.scalars(
            select(Usuario).order_by(Usuario.nombre, Usuario.email)
        ).all()

    return render_template("admin/usuarios.html", usuarios=usuarios)


@admin_bp.route("/moderacion", methods=["GET"])
@admin_required
def moderacion():
    session_factory = current_app.extensions["db_session_factory"]

    with session_factory() as session:
        preguntas = session.scalars(
            select(Pregunta)
            .options(
                selectinload(Pregunta.autor),
                selectinload(Pregunta.categoria),
            )
            .order_by(Pregunta.fecha_public.desc())
        ).all()

    return render_template("admin/moderacion.html", preguntas=preguntas)


@admin_bp.route("/preguntas/<uuid:pregunta_id>/eliminar", methods=["POST"])
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

    flash("La pregunta fue eliminada correctamente.", "success")
    return redirect(url_for("admin.moderacion"))
