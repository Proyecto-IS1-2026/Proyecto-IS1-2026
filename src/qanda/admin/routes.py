
from flask import current_app, render_template
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from qanda.admin import admin_bp
from qanda.auth.decorators import admin_required
from qanda.models import Pregunta, Usuario


@admin_bp.route("/usuarios", methods=["GET"])
@admin_required
def usuarios():
    session_factory = current_app.extensions["db_session_factory"]

    with session_factory() as session:
        usuarios = session.scalars(
            select(Usuario).order_by(
                Usuario.nombre,
                Usuario.email
            )
        ).all()

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios
    )


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
                selectinload(Pregunta.respuestas),
            )
            .order_by(Pregunta.fecha_public.desc())
        ).all()

    return render_template(
        "admin/moderacion.html",
        preguntas=preguntas
    )
