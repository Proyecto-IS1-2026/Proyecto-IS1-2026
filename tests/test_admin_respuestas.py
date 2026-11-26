import uuid

import pytest
from sqlalchemy import select

from qanda.admin.servicios import eliminar_respuesta as eliminar_respuesta_servicio
from qanda.models import Respuesta


class SesionEliminacion:
    def __init__(self):
        self.eliminados = []

    def delete(self, objeto):
        self.eliminados.append(objeto)


def test_admin_elimina_respuesta(
    client,
    admin,
    respuesta,
    db_session_factory,
    iniciar_sesion,
    flashes,
):
    iniciar_sesion(admin)

    response = client.post(f"/admin/respuestas/{respuesta.id}/eliminar")

    assert response.status_code == 302
    assert "/admin/moderacion" in response.headers["Location"]
    assert any(
        "La respuesta fue eliminada correctamente" in mensaje
        for _, mensaje in flashes()
    )

    with db_session_factory() as session:
        assert session.get(Respuesta, respuesta.id) is None


def test_usuario_general_no_puede_eliminar_respuesta(
    client,
    general,
    respuesta,
    db_session_factory,
    iniciar_sesion,
):
    iniciar_sesion(general)

    response = client.post(f"/admin/respuestas/{respuesta.id}/eliminar")

    assert response.status_code == 403

    with db_session_factory() as session:
        assert session.scalar(
            select(Respuesta).where(Respuesta.id == respuesta.id)
        ) is not None


def test_eliminar_respuesta_inexistente_da_404(
    client,
    admin,
    iniciar_sesion,
):
    iniciar_sesion(admin)

    response = client.post(f"/admin/respuestas/{uuid.uuid4()}/eliminar")

    assert response.status_code == 404


def test_servicio_eliminar_respuesta_verifica_permisos(general, respuesta):
    sesion = SesionEliminacion()

    with pytest.raises(PermissionError):
        eliminar_respuesta_servicio(sesion, respuesta, general)

    assert sesion.eliminados == []


def test_servicio_eliminar_respuesta_como_admin(admin, respuesta):
    sesion = SesionEliminacion()

    eliminar_respuesta_servicio(sesion, respuesta, admin)

    assert sesion.eliminados == [respuesta]
