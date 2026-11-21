import uuid

from sqlalchemy.orm import Session

from qanda import create_app
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
