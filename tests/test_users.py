import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash

from qanda import create_app
from qanda.models import Usuario


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

    yield aplicacion

    transaccion.rollback()
    conexion.close()


@pytest.fixture
def client(app):
    return app.test_client()


def obtener_flashes(client):
    with client.session_transaction() as sesion:
        return sesion.get("_flashes", [])


def test_create_user(client, app):
    email = f"ada-{uuid.uuid4().hex}@example.com"

    response = client.post(
        "/auth/register",
        data={
            "nombre": "Ada Lovelace",
            "email": f"  {email.upper()}  ",
            "password": "contraseña123",
            "confirmar_password": "contraseña123",
        },
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

    fabrica = app.extensions["db_session_factory"]

    with fabrica() as session:
        usuario = session.scalar(
            select(Usuario).where(Usuario.email == email)
        )

        assert usuario is not None
        assert usuario.nombre == "Ada Lovelace"
        assert usuario.email == email
        assert usuario.password_hash != "contraseña123"
        assert check_password_hash(
            usuario.password_hash,
            "contraseña123",
        )


def test_registro_con_email_duplicado(client, app):
    email = f"duplicado-{uuid.uuid4().hex}@example.com"

    fabrica = app.extensions["db_session_factory"]

    with fabrica.begin() as session:
        usuario = Usuario()
        usuario.registrarse(
            "Usuario existente",
            email,
            "contraseña123",
        )
        session.add(usuario)

    response = client.post(
        "/auth/register",
        data={
            "nombre": "Otro usuario",
            "email": email,
            "password": "contraseña123",
            "confirmar_password": "contraseña123",
        },
    )

    assert response.status_code == 302
    assert "/auth/register" in response.headers["Location"]
    assert any(
        "Ya existe un usuario" in mensaje
        for _, mensaje in obtener_flashes(client)
    )


def test_registro_con_contraseñas_diferentes(client):
    response = client.post(
        "/auth/register",
        data={
            "nombre": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "contraseña123",
            "confirmar_password": "contraseña456",
        },
    )

    assert response.status_code == 302
    assert "/auth/register" in response.headers["Location"]
    assert any(
        "no coinciden" in mensaje
        for _, mensaje in obtener_flashes(client)
    )


def test_registro_con_contraseña_corta(client):
    response = client.post(
        "/auth/register",
        data={
            "nombre": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "corta",
            "confirmar_password": "corta",
        },
    )

    assert response.status_code == 302
    assert "/auth/register" in response.headers["Location"]
    assert any(
        "al menos 8 caracteres" in mensaje
        for _, mensaje in obtener_flashes(client)
    )


def test_registro_con_email_invalido(client):
    response = client.post(
        "/auth/register",
        data={
            "nombre": "Ada Lovelace",
            "email": "email-invalido",
            "password": "contraseña123",
            "confirmar_password": "contraseña123",
        },
    )

    assert response.status_code == 302
    assert "/auth/register" in response.headers["Location"]
    assert any(
        "formato válido" in mensaje
        for _, mensaje in obtener_flashes(client)
    )


@pytest.mark.parametrize(
    ("nombre", "email", "password"),
    [
        ("", "ada@example.com", "contraseña123"),
        ("Ada", "", "contraseña123"),
        ("Ada", "ada@example.com", ""),
    ],
)
def test_registro_con_campos_obligatorios_vacios(
    client,
    nombre,
    email,
    password,
):
    response = client.post(
        "/auth/register",
        data={
            "nombre": nombre,
            "email": email,
            "password": password,
            "confirmar_password": password,
        },
    )

    assert response.status_code == 302
    assert "/auth/register" in response.headers["Location"]
    assert any(
        "Todos los campos son obligatorios" in mensaje
        for _, mensaje in obtener_flashes(client)
    )
