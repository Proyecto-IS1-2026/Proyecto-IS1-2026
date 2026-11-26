
import uuid

import pytest
from sqlalchemy import select
from werkzeug.security import check_password_hash

from qanda.models import Usuario


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


def test_registro_con_email_duplicado(client, app, flashes):
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
        for _, mensaje in flashes()
    )


def test_registro_con_contraseñas_diferentes(client, flashes):
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
        for _, mensaje in flashes()
    )


def test_registro_con_contraseña_corta(client, flashes):
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
        for _, mensaje in flashes()
    )


def test_registro_con_email_invalido(client, flashes):
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
        for _, mensaje in flashes()
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
    flashes,
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
        for _, mensaje in flashes()
    )
