from uuid import uuid4

import pytest


def test_listar_respuestas_vacias(entorno_respuestas):
    client, _, pregunta = entorno_respuestas
    respuesta = client.get(f"/api/preguntas/{pregunta.id}/respuestas")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


def test_crear_y_listar_respuesta(entorno_respuestas, iniciar_sesion):
    client, usuario, pregunta = entorno_respuestas
    iniciar_sesion(usuario)

    creada = client.post(
        f"/api/preguntas/{pregunta.id}/respuestas",
        json={"cuerpo": "  Respuesta de prueba  ", "autor_id": str(uuid4())},
    )
    assert creada.status_code == 201
    datos = creada.get_json()
    assert datos["cuerpo"] == "Respuesta de prueba"
    assert datos["autor_id"] == str(usuario.id)
    assert datos["pregunta_id"] == str(pregunta.id)
    assert datos["aceptacion"] is False
    assert datos["id"]
    assert datos["fecha_public"] is not None

    listado = client.get(f"/api/preguntas/{pregunta.id}/respuestas")
    assert listado.status_code == 200
    assert any(item["id"] == datos["id"] for item in listado.get_json())


def test_rechazar_respuesta_sin_sesion(entorno_respuestas):
    client, _, pregunta = entorno_respuestas
    respuesta = client.post(
        f"/api/preguntas/{pregunta.id}/respuestas",
        json={"cuerpo": "No debe guardarse"},
    )
    assert respuesta.status_code == 401


@pytest.mark.parametrize("cuerpo", ["", "   ", None, 123])
def test_rechazar_cuerpo_invalido(entorno_respuestas, iniciar_sesion, cuerpo):
    client, usuario, pregunta = entorno_respuestas
    iniciar_sesion(usuario)
    respuesta = client.post(
        f"/api/preguntas/{pregunta.id}/respuestas",
        json={"cuerpo": cuerpo},
    )
    assert respuesta.status_code == 400


def test_rechazar_json_invalido(entorno_respuestas, iniciar_sesion):
    client, usuario, pregunta = entorno_respuestas
    iniciar_sesion(usuario)
    respuesta = client.post(
        f"/api/preguntas/{pregunta.id}/respuestas",
        data="esto no es JSON",
        content_type="application/json",
    )
    assert respuesta.status_code == 400


def test_pregunta_inexistente(entorno_respuestas, iniciar_sesion):
    client, usuario, _ = entorno_respuestas
    iniciar_sesion(usuario)
    pregunta_id = uuid4()
    obtenida = client.get(f"/api/preguntas/{pregunta_id}/respuestas")
    creada = client.post(
        f"/api/preguntas/{pregunta_id}/respuestas",
        json={"cuerpo": "Respuesta sin pregunta"},
    )
    assert obtenida.status_code == 404
    assert creada.status_code == 404


def test_usuario_autenticado_inexistente(client):
    usuario_id = uuid4()

    with client.session_transaction() as sesion:
        sesion["usuario_id"] = str(usuario_id)

    respuesta = client.post(
        f"/api/preguntas/{uuid4()}/respuestas",
        json={"cuerpo": "Respuesta de usuario inexistente"},
    )

    assert respuesta.status_code == 401


def test_id_de_sesion_malformado(entorno_respuestas):
    client, _, pregunta = entorno_respuestas

    with client.session_transaction() as sesion:
        sesion["usuario_id"] = "no-es-un-uuid"

    respuesta = client.post(
        f"/api/preguntas/{pregunta.id}/respuestas",
        json={"cuerpo": "Respuesta con sesión inválida"},
    )

    assert respuesta.status_code == 401
