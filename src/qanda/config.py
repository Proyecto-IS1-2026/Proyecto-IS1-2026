
import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


def obtener_variable_obligatoria(nombre):
    valor = os.getenv(nombre)

    if not valor:
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
    pass


def obtener_configuracion():
    entorno = os.getenv("APP_ENV", "development").lower()

    configuraciones = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
    }

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

    if entorno not in configuraciones:
        raise ValueError(f"Entorno desconocido: {entorno}")

    return configuraciones[entorno]
