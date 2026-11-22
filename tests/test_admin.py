import uuid

import pytest

from qanda import create_app
from qanda.admin.servicios import eliminar_pregunta as eliminar_pregunta_servicio
from qanda.models import Categoria, Pregunta, Usuario


class ResultadoFalso:
    def __init__(self, filas):
        self._filas = filas

    def all(self):
        return list(self._filas)


class SesionFalsa:
    def __init__(self, fabrica):
        self.fabrica = fabrica

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def scalars(self, sentencia):
        descripciones = sentencia.column_descriptions
        entidad = descripciones[0]["entity"] if descripciones else None

        if entidad is Usuario:
            filas = self.fabrica.usuarios
        elif entidad is Pregunta:
            filas = self.fabrica.preguntas
        else:
            filas = []

        return ResultadoFalso(filas)

    def get(self, entidad, identificador):
        if entidad is Usuario:
            coleccion = self.fabrica.usuarios
        elif entidad is Pregunta:
            coleccion = self.fabrica.preguntas
        else:
            coleccion = []

        return next(
            (objeto for objeto in coleccion if objeto.id == identificador),
            None,
        )

    def delete(self, objeto):
        if isinstance(objeto, Pregunta) and objeto in self.fabrica.preguntas:
            self.fabrica.preguntas.remove(objeto)

        self.fabrica.eliminados.append(objeto)


class FabricaSesionesFalsas:
    def __init__(self, usuarios=(), preguntas=()):
        self.usuarios = list(usuarios)
        self.preguntas = list(preguntas)
        self.eliminados = []

    def __call__(self):
        return SesionFalsa(self)

    def begin(self):
        return self()


@pytest.fixture
def admin():
    usuario = Usuario(
        nombre="Ana Admin",
        email="ana.admin@example.com",
        password_hash="hash",
        rol="ADMIN",
    )
    usuario.id = uuid.uuid4()
    return usuario


@pytest.fixture
def general():
    usuario = Usuario(
        nombre="Gus General",
        email="gus.general@example.com",
        password_hash="hash",
        rol="GENERAL",
    )
    usuario.id = uuid.uuid4()
    return usuario


@pytest.fixture
def pregunta(admin):
    categoria = Categoria(nombre="Python", descrip="Preguntas de Python")
    categoria.id = uuid.uuid4()

    pregunta = Pregunta(
        titulo="¿Qué es Flask?",
        cuerpo="Quiero aprender Flask.",
        autor=admin,
        categoria=categoria,
    )
    pregunta.id = uuid.uuid4()
    return pregunta


@pytest.fixture
def fabrica(admin, general, pregunta):
    return FabricaSesionesFalsas(
        usuarios=[admin, general],
        preguntas=[pregunta],
    )


@pytest.fixture
def app(fabrica):
    aplicacion = create_app()
    aplicacion.config["TESTING"] = True
    aplicacion.config["SECRET_KEY"] = "clave-de-prueba"
    aplicacion.extensions["db_session_factory"] = fabrica
    return aplicacion


@pytest.fixture
def client(app):
    return app.test_client()


def iniciar_sesion(client, usuario):
    with client.session_transaction() as sesion:
        sesion["_user_id"] = str(usuario.id)
        sesion["_fresh"] = True


def test_admin_requiere_inicio_de_sesion(client):
    response = client.get("/admin/usuarios")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_usuario_general_no_puede_acceder(client, general):
    iniciar_sesion(client, general)

    assert client.get("/admin/usuarios").status_code == 403
    assert client.get("/admin/moderacion").status_code == 403


def test_admin_ve_listado_de_usuarios(client, admin):
    iniciar_sesion(client, admin)

    response = client.get("/admin/usuarios")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Ana Admin" in html
    assert "ana.admin@example.com" in html
    assert "ADMIN" in html
    assert "Gus General" in html
    assert "gus.general@example.com" in html
    assert "GENERAL" in html


def test_admin_ve_preguntas_para_moderar(client, admin):
    iniciar_sesion(client, admin)

    response = client.get("/admin/moderacion")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "¿Qué es Flask?" in html
    assert "Ana Admin" in html
    assert "Eliminar pregunta" in html


def test_admin_elimina_pregunta(client, admin, pregunta, fabrica):
    iniciar_sesion(client, admin)

    response = client.post(f"/admin/preguntas/{pregunta.id}/eliminar")

    assert response.status_code == 302
    assert "/admin/moderacion" in response.headers["Location"]
    assert pregunta not in fabrica.preguntas
    assert pregunta in fabrica.eliminados


def test_usuario_general_no_puede_eliminar(client, general, pregunta, fabrica):
    iniciar_sesion(client, general)

    response = client.post(f"/admin/preguntas/{pregunta.id}/eliminar")

    assert response.status_code == 403
    assert pregunta in fabrica.preguntas
    assert fabrica.eliminados == []


def test_eliminar_pregunta_inexistente_da_404(client, admin, fabrica):
    iniciar_sesion(client, admin)

    response = client.post(f"/admin/preguntas/{uuid.uuid4()}/eliminar")

    assert response.status_code == 404
    assert fabrica.eliminados == []


def test_servicio_verifica_permisos(general, pregunta):
    fabrica = FabricaSesionesFalsas(preguntas=[pregunta])

    with pytest.raises(PermissionError):
        eliminar_pregunta_servicio(fabrica(), pregunta, general)

    assert pregunta in fabrica.preguntas
    assert fabrica.eliminados == []
