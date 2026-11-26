import uuid

import pytest

from qanda.admin.servicios import eliminar_pregunta as eliminar_pregunta_servicio


@pytest.fixture(autouse=True)
def _fabrica_falsa(fabrica):
    return fabrica


def test_admin_requiere_inicio_de_sesion(client):
    response = client.get("/admin/usuarios")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_usuario_general_no_puede_acceder(client, general, iniciar_sesion):
    iniciar_sesion(general)

    assert client.get("/admin/usuarios").status_code == 403
    assert client.get("/admin/moderacion").status_code == 403


def test_admin_ve_listado_de_usuarios(client, admin, iniciar_sesion):
    iniciar_sesion(admin)

    response = client.get("/admin/usuarios")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Ana Admin" in html
    assert "ana.admin@example.com" in html
    assert "ADMIN" in html
    assert "Gus General" in html
    assert "gus.general@example.com" in html
    assert "GENERAL" in html


def test_admin_ve_preguntas_para_moderar(client, admin, iniciar_sesion):
    iniciar_sesion(admin)

    response = client.get("/admin/moderacion")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "¿Qué es Flask?" in html
    assert "Ana Admin" in html
    assert "Eliminar pregunta" in html


def test_admin_elimina_pregunta(client, admin, pregunta_falsa, fabrica, iniciar_sesion):
    iniciar_sesion(admin)

    response = client.post(f"/admin/preguntas/{pregunta_falsa.id}/eliminar")

    assert response.status_code == 302
    assert "/admin/moderacion" in response.headers["Location"]
    assert pregunta_falsa not in fabrica.preguntas
    assert pregunta_falsa in fabrica.eliminados


def test_usuario_general_no_puede_eliminar(
    client,
    general,
    pregunta_falsa,
    fabrica,
    iniciar_sesion,
):
    iniciar_sesion(general)

    response = client.post(f"/admin/preguntas/{pregunta_falsa.id}/eliminar")

    assert response.status_code == 403
    assert pregunta_falsa in fabrica.preguntas
    assert fabrica.eliminados == []


def test_eliminar_pregunta_inexistente_da_404(client, admin, fabrica, iniciar_sesion):
    iniciar_sesion(admin)

    response = client.post(f"/admin/preguntas/{uuid.uuid4()}/eliminar")

    assert response.status_code == 404
    assert fabrica.eliminados == []


def test_servicio_verifica_permisos(general, pregunta_falsa, fabrica):
    with pytest.raises(PermissionError):
        eliminar_pregunta_servicio(fabrica(), pregunta_falsa, general)

    assert pregunta_falsa in fabrica.preguntas
    assert fabrica.eliminados == []
