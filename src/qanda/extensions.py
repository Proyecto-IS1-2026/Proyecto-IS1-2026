import uuid

from flask import current_app
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

login_manager = LoginManager()


@login_manager.user_loader
def cargar_usuario(user_id):
    from qanda.models import Usuario

    try:
        usuario_id = uuid.UUID(user_id)
    except (ValueError, TypeError):
        return None

    session_factory = current_app.extensions["db_session_factory"]

    with session_factory() as session:
        return session.get(Usuario, usuario_id)


def init_db(app):
    engine = create_engine(
        app.config["DATABASE_URL"],
        pool_pre_ping=True,
    )

    app.extensions["db_engine"] = engine
    app.extensions["db_session_factory"] = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )


def init_login(app):
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
