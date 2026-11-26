import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from werkzeug.security import generate_password_hash

from qanda import create_app
from qanda.config import TestingConfig
from qanda.models import Base, Categoria, Etiqueta, Pregunta, Respuesta, Usuario

ESQUEMA = "is1"


@pytest.fixture(scope="session")
def test_database_url():
    """Crea una base PostgreSQL descartable y la elimina al finalizar la sesión."""
    valor = os.getenv("TEST_DATABASE_URL")

    if not valor:
        pytest.fail(
            "Definí TEST_DATABASE_URL con una conexión PostgreSQL que pueda "
            "crear bases de datos. Ejemplo: "
            "postgresql+psycopg://usuario:password@localhost:5432/postgres"
        )

    url_base = make_url(valor)
    nombre = f"qanda_test_{uuid.uuid4().hex}"
    identificador = nombre.replace('"', '""')
    url_prueba = url_base.set(database=nombre)

    motor_base = create_engine(
        url_base,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )

    try:
        with motor_base.connect() as conexion:
            conexion.execute(text(f'CREATE DATABASE "{identificador}"'))
    finally:
        motor_base.dispose()

    motor_ddl = create_engine(url_prueba, poolclass=NullPool)

    try:
        with motor_ddl.begin() as conexion:
            conexion.execute(text(f"CREATE SCHEMA {ESQUEMA}"))

        Base.metadata.create_all(motor_ddl)
    finally:
        motor_ddl.dispose()

    yield url_prueba

    motor_limpieza = create_engine(
        url_base,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )

    try:
        with motor_limpieza.connect() as conexion:
            conexion.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :nombre AND pid <> pg_backend_pid()"
                ),
                {"nombre": nombre},
            )
            conexion.execute(text(f'DROP DATABASE IF EXISTS "{identificador}"'))
    finally:
        motor_limpieza.dispose()


@pytest.fixture
def app(test_database_url):
    class ConfigPrueba(TestingConfig):
        TESTING = True
        SECRET_KEY = "clave-de-prueba"
        DATABASE_URL = test_database_url

    aplicacion = create_app(ConfigPrueba)
    engine = aplicacion.extensions["db_engine"]
    conexion = engine.connect()
    transaccion = conexion.begin()

    fabrica = sessionmaker(
        bind=conexion,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    aplicacion.extensions["db_session_factory"] = fabrica

    try:
        yield aplicacion
    finally:
        if transaccion.is_active:
            transaccion.rollback()
        conexion.close()
        engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session_factory(app):
    return app.extensions["db_session_factory"]


@pytest.fixture
def db_session(db_session_factory):
    with db_session_factory() as session:
        yield session
        session.rollback()


def _crear_usuario(fabrica, nombre, email, rol, password="contraseña123"):
    with fabrica.begin() as session:
        usuario = Usuario(
            nombre=nombre,
            email=email,
            password_hash=generate_password_hash(password),
            rol=rol,
        )
        session.add(usuario)
        session.flush()

    return usuario


@pytest.fixture
def usuario(db_session_factory):
    return _crear_usuario(
        db_session_factory,
        nombre="Usuario de prueba",
        email=f"usuario-{uuid.uuid4().hex}@example.com",
        rol="GENERAL",
    )


@pytest.fixture
def usuario_api(db_session_factory):
    return _crear_usuario(
        db_session_factory,
        nombre="Usuario API",
        email=f"api-{uuid.uuid4().hex}@example.com",
        rol="GENERAL",
    )


@pytest.fixture
def admin(db_session_factory):
    return _crear_usuario(
        db_session_factory,
        nombre="Ana Admin",
        email="ana.admin@example.com",
        rol="ADMIN",
    )


@pytest.fixture
def general(db_session_factory):
    return _crear_usuario(
        db_session_factory,
        nombre="Gus General",
        email="gus.general@example.com",
        rol="GENERAL",
    )


@pytest.fixture
def categoria(db_session_factory):
    with db_session_factory.begin() as session:
        categoria = Categoria(
            nombre="Python",
            descrip="Preguntas sobre Python",
        )
        session.add(categoria)
        session.flush()

    return categoria


@pytest.fixture
def etiqueta(db_session_factory):
    with db_session_factory.begin() as session:
        etiqueta = Etiqueta(nombre="Python")
        session.add(etiqueta)
        session.flush()

    return etiqueta


@pytest.fixture
def pregunta(admin, categoria, db_session_factory):
    with db_session_factory.begin() as session:
        autor = session.get(Usuario, admin.id)
        categoria_db = session.get(Categoria, categoria.id)

        pregunta = Pregunta(
            titulo="¿Qué es Flask?",
            cuerpo="Quiero aprender Flask.",
            autor=autor,
            categoria=categoria_db,
        )
        session.add(pregunta)
        session.flush()

    return pregunta


@pytest.fixture
def respuesta(pregunta, usuario, db_session_factory):
    with db_session_factory.begin() as session:
        pregunta_db = session.get(Pregunta, pregunta.id)
        autor = session.get(Usuario, usuario.id)

        respuesta = Respuesta(
            cuerpo="Respuesta de prueba",
            autor=autor,
            pregunta=pregunta_db,
        )
        session.add(respuesta)
        session.flush()

    return respuesta


@pytest.fixture
def iniciar_sesion(client):
    def _iniciar_sesion(usuario):
        with client.session_transaction() as sesion:
            sesion["_user_id"] = str(usuario.id)
            sesion["_fresh"] = True

    return _iniciar_sesion


@pytest.fixture
def flashes(client):
    def _flashes():
        with client.session_transaction() as sesion:
            return sesion.get("_flashes", [])

    return _flashes


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
def pregunta_falsa(admin):
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
def fabrica(app, admin, general, pregunta_falsa):
    fabrica = FabricaSesionesFalsas(
        usuarios=[admin, general],
        preguntas=[pregunta_falsa],
    )
    app.extensions["db_session_factory"] = fabrica
    return fabrica


@pytest.fixture
def entorno_respuestas(client, usuario, pregunta):
    return client, usuario, pregunta
