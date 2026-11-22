
import uuid
import pytest
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session, sessionmaker

from qanda import create_app
from qanda.extensions import cargar_usuario
from qanda.models import Autor, Usuario


def test_crear_usuario():
    app = create_app()
    engine = app.extensions["db_engine"]

    with engine.connect() as conexion:
        transaccion = conexion.begin()

        try:
            with Session(bind=conexion) as session:
                usuario = Usuario(
                    nombre="Usuario de prueba",
                    email=f"test-{uuid.uuid4().hex}@example.com",
                    password_hash="hash_de_prueba",
                    rol="GENERAL",
                )

                session.add(usuario)
                session.flush()

                usuario_id = usuario.id
                session.expire_all()

                assert session.get(Usuario, usuario_id) is not None
                assert session.get(Autor, usuario_id) is not None

            app.extensions["db_session_factory"] = sessionmaker(
                bind=conexion,
                expire_on_commit=False,
            )

            with app.app_context():
                usuario_recuperado = cargar_usuario(str(usuario_id))

                assert usuario_recuperado is not None
                assert usuario_recuperado.id == usuario_id

        finally:
            transaccion.rollback()


def test_relaciones_pregunta():
    from qanda.models import Categoria, Etiqueta, Pregunta, Respuesta

    app = create_app()
    engine = app.extensions["db_engine"]

    with engine.connect() as conexion:
        transaccion = conexion.begin()

        try:
            with Session(bind=conexion) as session:
                usuario = Usuario(
                    nombre="Usuario de prueba",
                    email=f"test-{uuid.uuid4().hex}@example.com",
                    password_hash="hash_de_prueba",
                    rol="GENERAL",
                )

                categoria = Categoria(
                    nombre="Programacion",
                    descrip="Preguntas sobre programacion",
                )

                etiqueta = Etiqueta(nombre="Python")

                pregunta = Pregunta(
                    titulo="¿Que es Flask?",
                    cuerpo="Quiero aprender Flask",
                    autor=usuario,
                    categoria=categoria,
                    etiquetas=[etiqueta],
                )

                respuesta = Respuesta(
                    cuerpo="Flask es un framework de Python",
                    autor=usuario,
                    pregunta=pregunta,
                )

                session.add_all([pregunta, respuesta])
                session.flush()

                pregunta_id = pregunta.id
                usuario_id = usuario.id

                session.expire_all()

                guardada = session.get(Pregunta, pregunta_id)

                assert guardada is not None
                assert guardada.autor.id == usuario_id
                assert guardada.categoria.nombre == "Programacion"
                assert len(guardada.etiquetas) == 1
                assert len(guardada.respuestas) == 1

        finally:
            transaccion.rollback()


def test_cargar_usuario_con_uuid_invalido():
    app = create_app()

    with app.app_context():
        usuario = cargar_usuario("esto-no-es-un-uuid")

        assert usuario is None


def test_rol_invalido():
    app = create_app()
    engine = app.extensions["db_engine"]

    with engine.connect() as conexion:
        transaccion = conexion.begin()

        try:
            with Session(bind=conexion) as session:
                usuario = Usuario(
                    nombre="Usuario de prueba",
                    email=f"test-{uuid.uuid4().hex}@example.com",
                    password_hash="hash_de_prueba",
                    rol="INVITADO",
                )

                session.add(usuario)

                with pytest.raises(IntegrityError) as error:
                    session.flush()

                assert (
                    error.value.orig.diag.constraint_name
                    == "ck_usuario_rol"
                )

        finally:
            transaccion.rollback()


def test_email_duplicado():
    app = create_app()
    engine = app.extensions["db_engine"]

    with engine.connect() as conexion:
        transaccion = conexion.begin()

        try:
            with Session(bind=conexion) as session:
                email = f"test-{uuid.uuid4().hex}@example.com"

                usuario1 = Usuario(
                    nombre="Usuario 1",
                    email=email,
                    password_hash="hash_de_prueba",
                    rol="GENERAL",
                )

                session.add(usuario1)
                session.flush()

                usuario2 = Usuario(
                    nombre="Usuario 2",
                    email=email,
                    password_hash="hash_de_prueba",
                    rol="GENERAL",
                )

                session.add(usuario2)

                with pytest.raises(IntegrityError):
                    session.flush()

        finally:
            if transaccion.is_active:
                transaccion.rollback()
