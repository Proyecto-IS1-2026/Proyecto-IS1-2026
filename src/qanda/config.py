
import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


def obtener_variable_obligatoria(nombre):
    valor = os.getenv(nombre)

    if valor is None or not valor.strip():
        raise ValueError(
            f"La variable de entorno {nombre} es obligatoria."
        )

    return valor


def crear_database_url(
    database_name,
    username=None,
    password=None,
):
    return URL.create(
        drivername="postgresql+psycopg",
        username=username or os.getenv("DB_USER", "is1_app"),
        password=(
            password
            if password is not None
            else os.getenv("DB_PASSWORD")
        ),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=database_name,
    )


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")


class DevelopmentConfig(Config):
    DATABASE_URL = crear_database_url(
        os.getenv("DB_NAME", "proyecto_is1_2026")
    )


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "clave-de-prueba"

    DATABASE_URL = crear_database_url(
        os.getenv("DB_TEST_NAME", "proyecto_is1_2026_test")
    )


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = None
    DATABASE_URL = None


def obtener_configuracion():
    entorno = os.getenv("APP_ENV", "development").lower()

    if entorno == "development":
        DevelopmentConfig.DATABASE_URL = crear_database_url(
            os.getenv("DB_NAME", "proyecto_is1_2026")
        )

        return DevelopmentConfig

    if entorno == "testing":
        TestingConfig.DATABASE_URL = crear_database_url(
            os.getenv("DB_TEST_NAME", "proyecto_is1_2026_test")
        )

        return TestingConfig

    if entorno == "production":
        ProductionConfig.SECRET_KEY = obtener_variable_obligatoria(
            "SECRET_KEY"
        )

        ProductionConfig.DATABASE_URL = crear_database_url(
            database_name=obtener_variable_obligatoria(
                "DB_PROD_NAME"
            ),
            username=obtener_variable_obligatoria(
                "DB_PROD_USER"
            ),
            password=obtener_variable_obligatoria(
                "DB_PROD_PASSWORD"
            ),
        )

        return ProductionConfig

    raise ValueError(f"Entorno desconocido: {entorno}")
