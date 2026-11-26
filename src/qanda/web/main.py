"""Rutas web para la publicación y consulta de preguntas y respuestas."""

from uuid import UUID

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import select

from qanda.models import Categoria, Etiqueta, Pregunta, Respuesta, Usuario
from qanda.services.sra import generar_respuesta_ia
from qanda.web import web_bp


@web_bp.route("/", methods=["GET"])
def index():
    """Muestra el listado de preguntas publicadas."""
    factory = current_app.extensions["db_session_factory"]

    with factory() as db:
        preguntas = db.scalars(
            select(Pregunta).order_by(Pregunta.fecha_public.desc())
        ).all()

        return render_template(
            "index.html",
            preguntas=preguntas,
        )


@web_bp.route("/preguntas/nueva", methods=["GET", "POST"])
def crear_pregunta():
    """Permite publicar una pregunta y solicitar una respuesta de IA."""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    factory = current_app.extensions["db_session_factory"]

    with factory() as db:
        categorias = db.scalars(
            select(Categoria).order_by(Categoria.nombre)
        ).all()

        etiquetas = db.scalars(
            select(Etiqueta).order_by(Etiqueta.nombre)
        ).all()

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            cuerpo = request.form.get("cuerpo", "").strip()
            categoria_id = request.form.get("categoria_id", "")
            proveedor_ia = request.form.get(
                "proveedor_ia", "ninguna"
            )

            if proveedor_ia not in ("ninguna", "openai", "gemini"):
                flash("El proveedor de IA seleccionado no es válido.", "error")

            elif not titulo or not cuerpo or len(titulo) > 255:
                flash(
                    "Completa correctamente el titulo y la descripcion.",
                    "error",
                )

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

                    if usuario is None:
                        abort(401)

                    pregunta = Pregunta.crear(
                        titulo=titulo,
                        cuerpo=cuerpo,
                        autor=usuario,
                        categoria=categoria,
                    )

                    for etiqueta_id in request.form.getlist(
                        "etiqueta_ids"
                    ):
                        try:
                            etiqueta_uuid = UUID(etiqueta_id)
                        except (ValueError, TypeError):
                            continue

                        etiqueta = db.get(Etiqueta, etiqueta_uuid)

                        if etiqueta is not None:
                            pregunta.agregarEtiqueta(etiqueta)

                    db.add(pregunta)
                    db.flush()

                    solicita_ia = any(
                        etiqueta.nombre == "IA-help"
                        for etiqueta in pregunta.etiquetas
                    )

                    if solicita_ia and proveedor_ia != "ninguna":
                        try:
                            generar_respuesta_ia(
                                db,
                                pregunta,
                                proveedor_ia,
                            )

                            flash(
                                "Pregunta publicada y respuesta de IA generada.",
                                "success",
                            )

                        except Exception:
                            current_app.logger.exception(
                                "Error al generar la respuesta de IA"
                            )

                            flash(
                                "La pregunta se publicó, pero no se pudo "
                                "generar la respuesta de IA.",
                                "warning",
                            )

                    elif solicita_ia:
                        flash(
                            "Pregunta publicada. No seleccionaste una IA.",
                            "success",
                        )

                    else:
                        flash(
                            "Pregunta publicada correctamente.",
                            "success",
                        )

                    db.commit()

                    return redirect(url_for("web.index"))

        return render_template(
            "preguntas/crear.html",
            categorias=categorias,
            etiquetas=etiquetas,
        )


@web_bp.route("/preguntas/<uuid:pregunta_id>", methods=["GET"])
def detalle_pregunta(pregunta_id):
    """Muestra una pregunta junto con sus respuestas."""
    factory = current_app.extensions["db_session_factory"]

    with factory() as db:
        pregunta = db.get(Pregunta, pregunta_id)

        if pregunta is None:
            abort(404)

        respuestas = db.scalars(
            select(Respuesta)
            .where(Respuesta.pregunta_id == pregunta_id)
            .order_by(
                Respuesta.fecha_public.asc(),
                Respuesta.id.asc(),
            )
        ).all()

        return render_template(
            "preguntas/detalle.html",
            pregunta=pregunta,
            respuestas=respuestas,
        )


@web_bp.route(
    "/preguntas/<uuid:pregunta_id>/responder",
    methods=["POST"],
)
def responder_pregunta(pregunta_id):
    """Registra una respuesta de un usuario a una pregunta."""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    cuerpo = request.form.get("cuerpo", "").strip()

    if not cuerpo:
        flash("La respuesta no puede estar vacía.", "error")
        return redirect(
            url_for("web.detalle_pregunta", pregunta_id=pregunta_id)
        )

    factory = current_app.extensions["db_session_factory"]

    with factory() as db:
        pregunta = db.get(Pregunta, pregunta_id)

        if pregunta is None:
            abort(404)

        usuario = db.get(
            Usuario,
            UUID(str(current_user.get_id())),
        )

        if usuario is None:
            abort(401)

        respuesta = Respuesta(
            cuerpo=cuerpo,
            autor=usuario,
            pregunta=pregunta,
        )

        db.add(respuesta)
        db.commit()

    flash("Respuesta publicada correctamente.", "success")

    return redirect(
        url_for("web.detalle_pregunta", pregunta_id=pregunta_id)
    )


@web_bp.route(
    "/preguntas/<uuid:pregunta_id>/respuestas/<uuid:respuesta_id>/aceptar",
    methods=["POST"],
)
def aceptar_respuesta(pregunta_id, respuesta_id):
    """Permite al autor de una pregunta aceptar una respuesta."""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    factory = current_app.extensions["db_session_factory"]

    with factory() as db:
        pregunta = db.get(Pregunta, pregunta_id)
        respuesta = db.get(Respuesta, respuesta_id)

        if pregunta is None or respuesta is None:
            abort(404)

        if respuesta.pregunta_id != pregunta.id:
            abort(404)

        usuario = db.get(
            Usuario,
            UUID(str(current_user.get_id())),
        )

        if usuario is None or pregunta.autor_id != usuario.id:
            abort(403)

        pregunta.aceptarRespuesta(respuesta, usuario)

        db.commit()

    flash("Respuesta aceptada correctamente.", "success")

    return redirect(
        url_for("web.detalle_pregunta", pregunta_id=pregunta_id)
    )
