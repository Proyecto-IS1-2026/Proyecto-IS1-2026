import uuid

import pytest
from sqlalchemy.orm import sessionmaker

from qanda import create_app
from qanda.models import Categoria, Usuario


@pytest.fixture
def app():
    aplicacion = create_app()
    aplicacion.config["TESTING"] = True
    aplicacion.config["SECRET_KEY"] = "clave-de-prueba"

    engine = aplicacion.extensions["db_engine"]
    conexion = engine.connect()
    transaccion = conexion.begin()

    fabrica = sessionmaker(
        bind=conexion,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    aplicacion.extensions["db_session_factory"] = fabrica

    with fabrica.begin() as session:
        usuario = Usuario(
            nombre="Usuario API",
            email=f"api-{uuid.uuid4().hex}@example.com",
            password_hash="hash-de-prueba",
            rol="GENERAL",
        )

        categoria = Categoria(
            nombre="Python",
            descrip="Preguntas sobre Python",
        )

        session.add_all([usuario, categoria])
        session.flush()

        aplicacion.config["TEST_USUARIO_ID"] = str(usuario.id)
        aplicacion.config["TEST_CATEGORIA_ID"] = str(categoria.id)

    yield aplicacion

    transaccion.rollback()
    conexion.close()


@pytest.fixture
def client(app):
    return app.test_client()


def iniciar_sesion(client, app):
    with client.session_transaction() as sesion:
        sesion["_user_id"] = app.config["TEST_USUARIO_ID"]
        sesion["_fresh"] = True


# POST /api/preguntas


def test_crear_pregunta_exitosamente(client, app):
    iniciar_sesion(client, app)

    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "¿Cómo funciona Flask?",
            "cuerpo": "Quiero aprender a desarrollar aplicaciones web.",
            "categoria_id": app.config["TEST_CATEGORIA_ID"],
        },
    )

    datos = response.get_json()

    assert response.status_code == 201
    assert datos["titulo"] == "¿Cómo funciona Flask?"
    assert datos["cuerpo"] == (
        "Quiero aprender a desarrollar aplicaciones web."
    )
    assert datos["autor"] == "Usuario API"
    assert datos["categoria"] == "Python"
    assert datos["id"] is not None
    assert datos["fecha_public"] is not None


def test_crear_pregunta_sin_autenticacion(client, app):
    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "Pregunta de prueba",
            "cuerpo": "Contenido de prueba",
            "categoria_id": app.config["TEST_CATEGORIA_ID"],
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "datos",
    [
        {
            "titulo": "",
            "cuerpo": "Contenido de prueba",
        },
        {
            "titulo": "Pregunta de prueba",
            "cuerpo": "",
        },
    ],
)
def test_crear_pregunta_con_datos_invalidos(client, app, datos):
    iniciar_sesion(client, app)

    datos_pregunta = {
        **datos,
        "categoria_id": app.config["TEST_CATEGORIA_ID"],
    }

    response = client.post(
        "/api/preguntas",
        json=datos_pregunta,
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_crear_pregunta_sin_categoria(client, app):
    iniciar_sesion(client, app)

    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "Pregunta de prueba",
            "cuerpo": "Contenido de prueba",
        },
    )

    assert response.status_code == 400


def test_crear_pregunta_con_categoria_inexistente(client, app):
    iniciar_sesion(client, app)

    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "Pregunta de prueba",
            "cuerpo": "Contenido de prueba",
            "categoria_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 404


def test_crear_pregunta_sin_json(client, app):
    iniciar_sesion(client, app)

    response = client.post("/api/preguntas")

    assert response.status_code == 400
    assert "error" in response.get_json()

# GET /api/preguntas


def test_listar_preguntas_sin_resultados(client):
    response = client.get("/api/preguntas")

    assert response.status_code == 200
    assert response.get_json() == []


def test_listar_preguntas_con_resultados(client, app):
    iniciar_sesion(client, app)

    response_creacion = client.post(
        "/api/preguntas",
        json={
            "titulo": "¿Cómo funciona Flask?",
            "cuerpo": "Quiero aprender Flask.",
            "categoria_id": app.config["TEST_CATEGORIA_ID"],
        },
    )

    assert response_creacion.status_code == 201

    response = client.get("/api/preguntas")
    datos = response.get_json()

    assert response.status_code == 200
    assert len(datos) == 1
    assert datos[0]["titulo"] == "¿Cómo funciona Flask?"
    assert datos[0]["cuerpo"] == "Quiero aprender Flask."
    assert datos[0]["autor"] == "Usuario API"
    assert datos[0]["categoria"] == "Python"
    assert datos[0]["id"] is not None
    assert datos[0]["fecha_public"] is not None

def test_obtener_pregunta_existente(client, app):
    iniciar_sesion(client, app)

    response_creacion = client.post(
        "/api/preguntas",
        json={
            "titulo": "¿Cómo funciona Flask?",
            "cuerpo": "Quiero aprender Flask.",
            "categoria_id": app.config["TEST_CATEGORIA_ID"],
        },
    )

    assert response_creacion.status_code == 201

    pregunta_id = response_creacion.get_json()["id"]

    response = client.get(f"/api/preguntas/{pregunta_id}")

    datos = response.get_json()

    assert response.status_code == 200
    assert datos["id"] == pregunta_id
    assert datos["titulo"] == "¿Cómo funciona Flask?"
    assert datos["cuerpo"] == "Quiero aprender Flask."
    assert datos["autor"] == "Usuario API"
    assert datos["categoria"] == "Python"
    assert datos["fecha_public"] is not None


def test_obtener_pregunta_inexistente(client):
    pregunta_id = uuid.uuid4()

    response = client.get(f"/api/preguntas/{pregunta_id}")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Pregunta no encontrada"
    }
