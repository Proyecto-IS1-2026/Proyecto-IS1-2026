import uuid

import pytest
from sqlalchemy.exc import SQLAlchemyError

# POST /api/preguntas


def test_crear_pregunta_exitosamente(
    client,
    usuario_api,
    categoria,
    iniciar_sesion,
):
    iniciar_sesion(usuario_api)

    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "¿Cómo funciona Flask?",
            "cuerpo": "Quiero aprender a desarrollar aplicaciones web.",
            "categoria_id": str(categoria.id),
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


def test_crear_pregunta_sin_autenticacion(client, categoria):
    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "Pregunta de prueba",
            "cuerpo": "Contenido de prueba",
            "categoria_id": str(categoria.id),
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
def test_crear_pregunta_con_datos_invalidos(
    client,
    usuario_api,
    categoria,
    iniciar_sesion,
    datos,
):
    iniciar_sesion(usuario_api)

    datos_pregunta = {
        **datos,
        "categoria_id": str(categoria.id),
    }

    response = client.post(
        "/api/preguntas",
        json=datos_pregunta,
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_crear_pregunta_sin_categoria(client, usuario_api, iniciar_sesion):
    iniciar_sesion(usuario_api)

    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "Pregunta de prueba",
            "cuerpo": "Contenido de prueba",
        },
    )

    assert response.status_code == 400


def test_crear_pregunta_con_categoria_inexistente(
    client,
    usuario_api,
    iniciar_sesion,
):
    iniciar_sesion(usuario_api)

    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "Pregunta de prueba",
            "cuerpo": "Contenido de prueba",
            "categoria_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize("categoria_id", ["no-es-un-uuid", 123, []])
def test_crear_pregunta_con_categoria_malformada(
    client,
    usuario_api,
    iniciar_sesion,
    categoria_id,
):
    iniciar_sesion(usuario_api)

    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "Pregunta de prueba",
            "cuerpo": "Contenido de prueba",
            "categoria_id": categoria_id,
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_crear_pregunta_sin_json(client, usuario_api, iniciar_sesion):
    iniciar_sesion(usuario_api)

    response = client.post("/api/preguntas")

    assert response.status_code == 400
    assert "error" in response.get_json()


# GET /api/preguntas


def test_listar_preguntas_sin_resultados(client):
    response = client.get("/api/preguntas")

    assert response.status_code == 200
    assert response.get_json() == []


def test_listar_preguntas_con_resultados(
    client,
    usuario_api,
    categoria,
    iniciar_sesion,
):
    iniciar_sesion(usuario_api)

    response_creacion = client.post(
        "/api/preguntas",
        json={
            "titulo": "¿Cómo funciona Flask?",
            "cuerpo": "Quiero aprender Flask.",
            "categoria_id": str(categoria.id),
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


def test_obtener_pregunta_existente(
    client,
    usuario_api,
    categoria,
    iniciar_sesion,
):
    iniciar_sesion(usuario_api)

    response_creacion = client.post(
        "/api/preguntas",
        json={
            "titulo": "¿Cómo funciona Flask?",
            "cuerpo": "Quiero aprender Flask.",
            "categoria_id": str(categoria.id),
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


# Errores de base de datos


class FabricaConError:
    def __call__(self):
        raise SQLAlchemyError("falló la consulta")


class FabricaConErrorAlCrear:
    def __init__(self, fabrica_real):
        self.fabrica_real = fabrica_real

    def __call__(self):
        return self.fabrica_real()

    def begin(self):
        raise SQLAlchemyError("falló la consulta")


def test_error_de_base_al_crear_pregunta(
    client,
    app,
    usuario_api,
    categoria,
    iniciar_sesion,
):
    iniciar_sesion(usuario_api)
    app.extensions["db_session_factory"] = FabricaConErrorAlCrear(
        app.extensions["db_session_factory"]
    )

    response = client.post(
        "/api/preguntas",
        json={
            "titulo": "Pregunta de prueba",
            "cuerpo": "Contenido de prueba",
            "categoria_id": str(categoria.id),
        },
    )

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "No se pudo crear la pregunta"
    }


def test_error_de_base_al_listar_preguntas(client, app):
    app.extensions["db_session_factory"] = FabricaConError()

    response = client.get("/api/preguntas")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "No se pudieron obtener las preguntas"
    }


def test_error_de_base_al_obtener_pregunta(client, app):
    app.extensions["db_session_factory"] = FabricaConError()

    response = client.get(f"/api/preguntas/{uuid.uuid4()}")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "No se pudo obtener la pregunta"
    }
