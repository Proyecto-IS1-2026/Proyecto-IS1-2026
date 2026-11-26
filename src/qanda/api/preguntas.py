from uuid import UUID

from flask import current_app, jsonify, request
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from qanda.api import api_bp
from qanda.models import Categoria, Pregunta, Usuario


@api_bp.route("/preguntas", methods=["POST"])
def crear_pregunta():
    if not current_user.is_authenticated:
        return jsonify({"error": "Debés iniciar sesión"}), 401

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Se requiere un objeto JSON"}), 400

    session_factory = current_app.extensions["db_session_factory"]

    try:
        with session_factory.begin() as session:
            categoria_id = datos.get("categoria_id")

            usuario = session.get(Usuario, current_user.id)

            if usuario is None:
                return jsonify({"error": "Usuario no encontrado"}), 401

            if not categoria_id:
                return jsonify({"error": "La categoría es obligatoria"}), 400

            try:
                categoria_uuid = UUID(str(categoria_id))
            except (TypeError, ValueError):
                return jsonify({"error": "La categoría no es válida"}), 400

            categoria = session.get(Categoria, categoria_uuid)

            if categoria is None:
                return jsonify({"error": "La categoría no existe"}), 404

            pregunta = Pregunta.crear(
                titulo=datos.get("titulo"),
                cuerpo=datos.get("cuerpo"),
                autor=usuario,
                categoria=categoria,
            )

            session.add(pregunta)
            session.flush()
            session.refresh(pregunta)

            respuesta = {
                "id": str(pregunta.id),
                "titulo": pregunta.titulo,
                "cuerpo": pregunta.cuerpo,
                "autor": pregunta.autor.nombre,
                "categoria": pregunta.categoria.nombre,
                "fecha_public": pregunta.fecha_public.isoformat(),
            }

        return jsonify(respuesta), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except (SQLAlchemyError, TypeError):
        return jsonify({"error": "No se pudo crear la pregunta"}), 500


@api_bp.route("/preguntas", methods=["GET"])
def listar_preguntas():
    session_factory = current_app.extensions["db_session_factory"]

    try:
        with session_factory() as session:
            sentencia = (
                select(Pregunta)
                .order_by(Pregunta.fecha_public.desc())
            )

            preguntas = session.scalars(sentencia).all()

            resultado = [
                {
                    "id": str(pregunta.id),
                    "titulo": pregunta.titulo,
                    "cuerpo": pregunta.cuerpo,
                    "autor": pregunta.autor.nombre,
                    "categoria": pregunta.categoria.nombre,
                    "fecha_public": pregunta.fecha_public.isoformat(),
                }
                for pregunta in preguntas
            ]

        return jsonify(resultado), 200

    except SQLAlchemyError:
        return jsonify(
            {"error": "No se pudieron obtener las preguntas"}
        ), 500

@api_bp.route("/preguntas/<uuid:pregunta_id>", methods=["GET"])
def obtener_pregunta(pregunta_id):
    session_factory = current_app.extensions["db_session_factory"]

    try:
        with session_factory() as session:
            pregunta = session.get(Pregunta, pregunta_id)

            if pregunta is None:
                return jsonify({"error": "Pregunta no encontrada"}), 404

            resultado = {
                "id": str(pregunta.id),
                "titulo": pregunta.titulo,
                "cuerpo": pregunta.cuerpo,
                "autor": pregunta.autor.nombre,
                "categoria": pregunta.categoria.nombre,
                "fecha_public": pregunta.fecha_public.isoformat(),
            }

        return jsonify(resultado), 200

    except SQLAlchemyError:
        return jsonify(
            {"error": "No se pudo obtener la pregunta"}
        ), 500
