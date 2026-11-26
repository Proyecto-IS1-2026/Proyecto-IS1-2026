import uuid

from sqlalchemy import select

from qanda.models import Categoria, Pregunta, Respuesta, Usuario


def test_index_sin_preguntas(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "¿Qué es Flask?" not in response.get_data(as_text=True)


def test_index_con_preguntas(client, pregunta):
    response = client.get("/")

    assert response.status_code == 200
    assert "¿Qué es Flask?" in response.get_data(as_text=True)


def test_crear_pregunta_requiere_sesion(client):
    response = client.get("/preguntas/nueva")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_crear_pregunta_get_autenticado(client, usuario, iniciar_sesion):
    iniciar_sesion(usuario)

    assert client.get("/preguntas/nueva").status_code == 200


def test_crear_pregunta_post_valida(
    client,
    usuario,
    categoria,
    etiqueta,
    db_session_factory,
    iniciar_sesion,
    flashes,
):
    iniciar_sesion(usuario)

    response = client.post(
        "/preguntas/nueva",
        data={
            "titulo": "  ¿Cómo usar Flask?  ",
            "cuerpo": "  Quiero un ejemplo  ",
            "categoria_id": str(categoria.id),
            "etiqueta_ids": str(etiqueta.id),
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert any(
        "Pregunta publicada correctamente" in mensaje
        for _, mensaje in flashes()
    )

    with db_session_factory() as session:
        guardada = session.scalar(
            select(Pregunta).where(Pregunta.titulo == "¿Cómo usar Flask?")
        )

        assert guardada is not None
        assert guardada.cuerpo == "Quiero un ejemplo"
        assert [tag.id for tag in guardada.etiquetas] == [etiqueta.id]


def test_crear_pregunta_post_titulo_invalido(
    client,
    usuario,
    categoria,
    db_session_factory,
    iniciar_sesion,
):
    iniciar_sesion(usuario)

    response = client.post(
        "/preguntas/nueva",
        data={
            "titulo": "   ",
            "cuerpo": "Contenido",
            "categoria_id": str(categoria.id),
        },
    )

    assert response.status_code == 200
    assert (
        "Completa correctamente el titulo y la descripcion."
        in response.get_data(as_text=True)
    )

    with db_session_factory() as session:
        assert session.scalar(select(Pregunta)) is None


def test_crear_pregunta_post_categoria_invalida(
    client,
    usuario,
    iniciar_sesion,
):
    iniciar_sesion(usuario)

    response = client.post(
        "/preguntas/nueva",
        data={
            "titulo": "Pregunta válida",
            "cuerpo": "Contenido",
            "categoria_id": "no-es-un-uuid",
        },
    )

    assert response.status_code == 200
    assert (
        "Selecciona una categoría valida."
        in response.get_data(as_text=True)
    )


def test_crear_pregunta_ignora_etiquetas_invalidas(
    client,
    usuario,
    categoria,
    db_session_factory,
    iniciar_sesion,
):
    iniciar_sesion(usuario)

    response = client.post(
        "/preguntas/nueva",
        data={
            "titulo": "Pregunta sin etiquetas válidas",
            "cuerpo": "Contenido",
            "categoria_id": str(categoria.id),
            "etiqueta_ids": "no-es-un-uuid",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with db_session_factory() as session:
        guardada = session.scalar(
            select(Pregunta).where(
                Pregunta.titulo == "Pregunta sin etiquetas válidas"
            )
        )

        assert guardada is not None
        assert guardada.etiquetas == []


def test_detalle_pregunta(client, pregunta):
    response = client.get(f"/preguntas/{pregunta.id}")

    assert response.status_code == 200
    assert "¿Qué es Flask?" in response.get_data(as_text=True)


def test_detalle_pregunta_inexistente(client):
    assert client.get(f"/preguntas/{uuid.uuid4()}").status_code == 404


def test_responder_pregunta_requiere_sesion(client, pregunta):
    response = client.post(
        f"/preguntas/{pregunta.id}/responder",
        data={"cuerpo": "Una respuesta"},
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_responder_pregunta_cuerpo_vacio(
    client,
    usuario,
    pregunta,
    iniciar_sesion,
    flashes,
):
    iniciar_sesion(usuario)

    response = client.post(
        f"/preguntas/{pregunta.id}/responder",
        data={"cuerpo": "   "},
    )

    assert response.status_code == 302
    assert str(pregunta.id) in response.headers["Location"]
    assert any(
        "La respuesta no puede estar vacía" in mensaje
        for _, mensaje in flashes()
    )


def test_responder_pregunta_valida(
    client,
    usuario,
    pregunta,
    db_session_factory,
    iniciar_sesion,
    flashes,
):
    iniciar_sesion(usuario)

    response = client.post(
        f"/preguntas/{pregunta.id}/responder",
        data={"cuerpo": "Flask es un framework"},
    )

    assert response.status_code == 302
    assert str(pregunta.id) in response.headers["Location"]
    assert any(
        "Respuesta publicada correctamente" in mensaje
        for _, mensaje in flashes()
    )

    with db_session_factory() as session:
        respuesta = session.scalar(
            select(Respuesta).where(Respuesta.cuerpo == "Flask es un framework")
        )

        assert respuesta is not None
        assert respuesta.pregunta_id == pregunta.id
        assert respuesta.autor_id == usuario.id


def test_responder_pregunta_inexistente(client, usuario, iniciar_sesion):
    iniciar_sesion(usuario)

    response = client.post(
        f"/preguntas/{uuid.uuid4()}/responder",
        data={"cuerpo": "Una respuesta"},
    )

    assert response.status_code == 404


def test_aceptar_respuesta_requiere_sesion(client, pregunta, respuesta):
    response = client.post(
        f"/preguntas/{pregunta.id}/respuestas/{respuesta.id}/aceptar"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_aceptar_respuesta_por_no_autor(
    client,
    usuario,
    pregunta,
    respuesta,
    iniciar_sesion,
):
    iniciar_sesion(usuario)

    response = client.post(
        f"/preguntas/{pregunta.id}/respuestas/{respuesta.id}/aceptar"
    )

    assert response.status_code == 403


def test_aceptar_respuesta_por_autor(
    client,
    admin,
    pregunta,
    respuesta,
    db_session_factory,
    iniciar_sesion,
    flashes,
):
    iniciar_sesion(admin)

    response = client.post(
        f"/preguntas/{pregunta.id}/respuestas/{respuesta.id}/aceptar"
    )

    assert response.status_code == 302
    assert str(pregunta.id) in response.headers["Location"]
    assert any(
        "Respuesta aceptada correctamente" in mensaje
        for _, mensaje in flashes()
    )

    with db_session_factory() as session:
        guardada = session.get(Respuesta, respuesta.id)

        assert guardada.aceptacion is True


def test_aceptar_respuesta_de_otra_pregunta(
    client,
    admin,
    pregunta,
    categoria,
    db_session_factory,
    iniciar_sesion,
):
    with db_session_factory.begin() as session:
        otra = Pregunta(
            titulo="Otra pregunta",
            cuerpo="Otro cuerpo",
            autor=session.get(Usuario, admin.id),
            categoria=session.get(Categoria, categoria.id),
        )
        session.add(otra)
        session.flush()

        otra_respuesta = Respuesta(
            cuerpo="Respuesta de la otra pregunta",
            autor=session.get(Usuario, admin.id),
            pregunta=otra,
        )
        session.add(otra_respuesta)
        session.flush()

        otra_respuesta_id = otra_respuesta.id

    iniciar_sesion(admin)

    response = client.post(
        f"/preguntas/{pregunta.id}/respuestas/{otra_respuesta_id}/aceptar"
    )

    assert response.status_code == 404


def test_aceptar_respuesta_inexistente(
    client,
    admin,
    pregunta,
    iniciar_sesion,
):
    iniciar_sesion(admin)

    response = client.post(
        f"/preguntas/{pregunta.id}/respuestas/{uuid.uuid4()}/aceptar"
    )

    assert response.status_code == 404
