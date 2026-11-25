from uuid import uuid4

import pytest
from sqlalchemy.orm import sessionmaker

from qanda.models import Categoria, Pregunta, Usuario


@pytest.fixture
def entorno_respuestas(client):
    app = client.application
    engine = app.extensions["db_engine"]
    factory_original = app.extensions["db_session_factory"]
    secret_original = app.config.get("SECRET_KEY")
    if not secret_original:
        app.config["SECRET_KEY"] = "clave-de-tests"

    conexion = engine.connect()
    transaccion = conexion.begin()
    factory = sessionmaker(
        bind=conexion,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    app.extensions["db_session_factory"] = factory

    usuario_id = uuid4()
    pregunta_id = uuid4()

    try:
        with factory() as db:
            usuario = Usuario(
                id=usuario_id,
                nombre="Autor de prueba",
                email=f"prueba-{uuid4().hex}@example.com",
                password_hash="hash-para-tests",
                rol="GENERAL",
            )
            categoria = Categoria(
                id=uuid4(),
                nombre=f"Categoría-{uuid4().hex[:8]}",
                descrip="Categoría para tests",
            )
            pregunta = Pregunta(
                id=pregunta_id,
                titulo="Pregunta de prueba",
                cuerpo="¿Como se responde?",
                autor=usuario,
                categoria=categoria,
            )
            db.add_all([usuario, categoria, pregunta])
            db.commit()

        yield client, usuario_id, pregunta_id
    finally:
        app.extensions["db_session_factory"] = factory_original
        if transaccion.is_active:
            transaccion.rollback()
        conexion.close()
        app.config["SECRET_KEY"] = secret_original


def _autenticar(client, usuario_id):
    with client.session_transaction() as sesion:
      
        sesion["_user_id"] = str(usuario_id)
        sesion["_fresh"] = True
       
        sesion["usuario_id"] = str(usuario_id)
        sesion["user_id"] = str(usuario_id)


def test_listar_respuestas_vacias(entorno_respuestas):
    client, _, pregunta_id = entorno_respuestas
    respuesta = client.get(f"/api/preguntas/{pregunta_id}/respuestas")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


def test_crear_y_listar_respuesta(entorno_respuestas):
    client, usuario_id, pregunta_id = entorno_respuestas
    _autenticar(client, usuario_id)

    creada = client.post(
        f"/api/preguntas/{pregunta_id}/respuestas",
        json={"cuerpo": "  Respuesta de prueba  ", "autor_id": str(uuid4())},
    )
    assert creada.status_code == 201
    datos = creada.get_json()
    assert datos["cuerpo"] == "Respuesta de prueba"
    assert datos["autor_id"] == str(usuario_id)
    assert datos["pregunta_id"] == str(pregunta_id)
    assert datos["aceptacion"] is False
    assert datos["id"]
    assert datos["fecha_public"] is not None

    listado = client.get(f"/api/preguntas/{pregunta_id}/respuestas")
    assert listado.status_code == 200
    assert any(item["id"] == datos["id"] for item in listado.get_json())


def test_rechazar_respuesta_sin_sesion(entorno_respuestas):
    client, _, pregunta_id = entorno_respuestas
    respuesta = client.post(
        f"/api/preguntas/{pregunta_id}/respuestas",
        json={"cuerpo": "No debe guardarse"},
    )
    assert respuesta.status_code == 401


@pytest.mark.parametrize("cuerpo", ["", "   ", None, 123])
def test_rechazar_cuerpo_invalido(entorno_respuestas, cuerpo):
    client, usuario_id, pregunta_id = entorno_respuestas
    _autenticar(client, usuario_id)
    respuesta = client.post(
        f"/api/preguntas/{pregunta_id}/respuestas",
        json={"cuerpo": cuerpo},
    )
    assert respuesta.status_code == 400


def test_rechazar_json_invalido(entorno_respuestas):
    client, usuario_id, pregunta_id = entorno_respuestas
    _autenticar(client, usuario_id)
    respuesta = client.post(
        f"/api/preguntas/{pregunta_id}/respuestas",
        data="esto no es JSON",
        content_type="application/json",
    )
    assert respuesta.status_code == 400


def test_pregunta_inexistente(entorno_respuestas):
    client, usuario_id, _ = entorno_respuestas
    _autenticar(client, usuario_id)
    pregunta_id = uuid4()
    obtenida = client.get(f"/api/preguntas/{pregunta_id}/respuestas")
    creada = client.post(
        f"/api/preguntas/{pregunta_id}/respuestas",
        json={"cuerpo": "Respuesta sin pregunta"},
    )
    assert obtenida.status_code == 404
    assert creada.status_code == 404