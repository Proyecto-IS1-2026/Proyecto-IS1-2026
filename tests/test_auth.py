import pytest


def test_get_login_y_registro_renderizan(client):
    assert client.get("/auth/login").status_code == 200
    assert client.get("/auth/register").status_code == 200


def test_login_exitoso(client, usuario, flashes):
    response = client.post(
        "/auth/login",
        data={
            "email": f"  {usuario.email.upper()}  ",
            "password": "contraseña123",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with client.session_transaction() as sesion:
        assert sesion["_user_id"] == str(usuario.id)

    assert any(
        "Iniciaste sesión correctamente" in mensaje
        for _, mensaje in flashes()
    )


def test_login_con_password_incorrecto(client, usuario, flashes):
    response = client.post(
        "/auth/login",
        data={"email": usuario.email, "password": "incorrecta"},
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert any(
        "Email o contraseña incorrectos" in mensaje
        for _, mensaje in flashes()
    )


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("", "contraseña123"),
        ("ada@example.com", ""),
    ],
)
def test_login_con_campos_vacios(client, email, password, flashes):
    response = client.post(
        "/auth/login",
        data={"email": email, "password": password},
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert any(
        "Debés ingresar email y contraseña" in mensaje
        for _, mensaje in flashes()
    )


def test_logout_requiere_sesion(client):
    response = client.post("/auth/logout")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_logout_cierra_la_sesion(client, usuario, iniciar_sesion, flashes):
    iniciar_sesion(usuario)

    response = client.post("/auth/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with client.session_transaction() as sesion:
        assert "_user_id" not in sesion

    assert any(
        "Cerraste sesión correctamente" in mensaje
        for _, mensaje in flashes()
    )
