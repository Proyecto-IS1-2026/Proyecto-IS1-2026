from flask import render_template

from qanda.web import web_bp


from uuid import UUID

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import select

from qanda.models import Categoria, Pregunta, Usuario
from qanda.web import web_bp


@web_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@web_bp.route("/preguntas/nueva", methods=["GET", "POST"])
def crear_pregunta():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    factory = current_app.extensions["db_session_factory"]

    with factory() as db:
        categorias = db.scalars(
            select(Categoria).order_by(Categoria.nombre)
        ).all()

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            cuerpo = request.form.get("cuerpo", "").strip()
            categoria_id = request.form.get("categoria_id", "")

            if not titulo or not cuerpo or len(titulo) > 255:
                flash("Completa correctamente el titulo y la descripcion.", "error")

            else:
                try:
                    categoria_uuid = UUID(categoria_id)
                except (ValueError, TypeError):
                    categoria_uuid = None

                categoria = (
                    db.get(Categoria, categoria_uuid)
                    if categoria_uuid is not None
                    else None
                )

                if categoria is None:
                    flash("Selecciona una categoría valida.", "error")
                else:
                    usuario = db.get(
                        Usuario,
                        UUID(str(current_user.get_id())),
                    )

                    pregunta = Pregunta.crear(
                        titulo=titulo,
                        cuerpo=cuerpo,
                        autor=usuario,
                        categoria=categoria,
                    )

                    db.add(pregunta)
                    db.commit()

                    flash("Pregunta publicada correctamente.", "success")
                    return redirect(url_for("web.index"))

        return render_template(
            "preguntas/crear.html",
            categorias=categorias,
        )