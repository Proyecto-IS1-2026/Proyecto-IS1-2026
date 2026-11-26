"""Configuraciones de la aplicación según el entorno de ejecución."""

import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

# Carga las variables definidas en el archivo .env, si está disponible.
load_dotenv()


def obtener_variable_obligatoria(nombre):
    """Obtiene una variable de entorno y verifica que tenga un valor."""
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
    """Construye la URL de conexión a PostgreSQL.

    Utiliza los valores recibidos o, cuando no se proporcionan,
    los correspondientes a las variables de entorno.
    """
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
    """Configuración base compartida por los distintos entornos."""

    SECRET_KEY = os.getenv("SECRET_KEY")


class DevelopmentConfig(Config):
    """Configuración para el entorno de desarrollo."""

    DATABASE_URL = crear_database_url(
        os.getenv("DB_NAME", "proyecto_is1_2026")
    )


class TestingConfig(Config):
    """Configuración utilizada durante las pruebas automatizadas."""

    TESTING = True
    SECRET_KEY = "clave-de-prueba"

    DATABASE_URL = crear_database_url(
        os.getenv("DB_TEST_NAME", "proyecto_is1_2026_test")
    )


class ProductionConfig(Config):
    """Configuración para la ejecución en producción."""

    DEBUG = False
    TESTING = False
    SECRET_KEY = None
    DATABASE_URL = None


def obtener_configuracion():
    """Selecciona y prepara la configuración según APP_ENV.

    En producción se validan explícitamente las credenciales
    necesarias para conectarse a la base de datos.
    """
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
