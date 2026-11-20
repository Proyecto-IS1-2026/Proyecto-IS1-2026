from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
