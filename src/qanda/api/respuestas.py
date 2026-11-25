#Endpoints para crear y consultar respuestas de una pregunta.

from uuid import UUID

from flask import current_app, jsonify, request, session as flask_session
from flask_login import current_user
from sqlalchemy import select

from qanda.api import api_bp
from qanda.models import Pregunta, Respuesta, Usuario


def _serializar_respuesta(respuesta: Respuesta) -> dict[str, str | bool | None]:
    return {
        "id": str(respuesta.id),
        "cuerpo": respuesta.cuerpo,
        "fecha_public": (
            respuesta.fecha_public.isoformat() if respuesta.fecha_public else None
        ),
        "aceptacion": respuesta.aceptacion,
        "autor_id": str(respuesta.autor_id),
        "pregunta_id": str(respuesta.pregunta_id),
    }


def _id_usuario_autenticado() -> UUID | None:
    #Utiliza Flask-Login; admite las claves de sesión del proyecto si se usan.
    if getattr(current_user, "is_authenticated", False):
        identificador = current_user.get_id()
    else:
        identificador = flask_session.get("usuario_id") or flask_session.get("user_id")

    if not identificador:
        return None

    try:
        return UUID(str(identificador))
    except (TypeError, ValueError, AttributeError):
        return None


@api_bp.post("/preguntas/<uuid:pregunta_id>/respuestas")
def crear_respuesta(pregunta_id: UUID):
    usuario_id = _id_usuario_autenticado()
    if usuario_id is None:
        return jsonify({"error": "Debes iniciar sesión para responder."}), 401

    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"error": "Se espera un objeto JSON válido."}), 400

    cuerpo = datos.get("cuerpo")
    if not isinstance(cuerpo, str) or not cuerpo.strip():
        return jsonify({"error": "El cuerpo de la respuesta es obligatorio."}), 400

    with current_app.extensions["db_session_factory"]() as db:
        usuario = db.get(Usuario, usuario_id)
        if usuario is None:
            return jsonify({"error": "El usuario autenticado no existe."}), 401

        pregunta = db.get(Pregunta, pregunta_id)
        if pregunta is None:
            return jsonify({"error": "La pregunta no existe."}), 404

        respuesta = Respuesta(
            cuerpo=cuerpo.strip(),
            autor_id=usuario.id,
            pregunta_id=pregunta.id,
        )
        db.add(respuesta)
        db.commit()
        db.refresh(respuesta)
        return jsonify(_serializar_respuesta(respuesta)), 201


@api_bp.get("/preguntas/<uuid:pregunta_id>/respuestas")
def listar_respuestas(pregunta_id: UUID):
    with current_app.extensions["db_session_factory"]() as db:
        if db.get(Pregunta, pregunta_id) is None:
            return jsonify({"error": "La pregunta no existe."}), 404

        respuestas = db.scalars(
            select(Respuesta)
            .where(Respuesta.pregunta_id == pregunta_id)
            .order_by(Respuesta.fecha_public.asc(), Respuesta.id.asc())
        ).all()
        return jsonify([_serializar_respuesta(r) for r in respuestas]), 200