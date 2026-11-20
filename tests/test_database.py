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
