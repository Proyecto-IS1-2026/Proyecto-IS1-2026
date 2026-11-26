import pytest

from qanda.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    crear_database_url,
    obtener_configuracion,
    obtener_variable_obligatoria,
)


@pytest.fixture(autouse=True)
def _restaurar_configuracion_produccion():
    secreto_original = ProductionConfig.SECRET_KEY
    url_original = getattr(ProductionConfig, "DATABASE_URL", None)

    yield

    ProductionConfig.SECRET_KEY = secreto_original

    if url_original is None:
        if hasattr(ProductionConfig, "DATABASE_URL"):
            delattr(ProductionConfig, "DATABASE_URL")
    else:
        ProductionConfig.DATABASE_URL = url_original


@pytest.mark.parametrize(
    ("entorno", "configuracion"),
    [
        ("development", DevelopmentConfig),
        ("testing", TestingConfig),
        ("DEVELOPMENT", DevelopmentConfig),
    ],
)
def test_configuracion_segun_entorno(monkeypatch, entorno, configuracion):
    monkeypatch.setenv("APP_ENV", entorno)

    assert obtener_configuracion() is configuracion


def test_configuracion_desconocida(monkeypatch):
    monkeypatch.setenv("APP_ENV", "desconocido")

    with pytest.raises(ValueError, match="Entorno desconocido"):
        obtener_configuracion()


def test_obtener_variable_obligatoria(monkeypatch):
    monkeypatch.setenv("VARIABLE_DE_PRUEBA", "valor")

    assert obtener_variable_obligatoria("VARIABLE_DE_PRUEBA") == "valor"

    monkeypatch.delenv("VARIABLE_DE_PRUEBA")

    with pytest.raises(ValueError, match="VARIABLE_DE_PRUEBA"):
        obtener_variable_obligatoria("VARIABLE_DE_PRUEBA")


def test_crear_database_url_con_valores_explicitos(monkeypatch):
    monkeypatch.setenv("DB_HOST", "servidor")
    monkeypatch.setenv("DB_PORT", "6543")

    url = crear_database_url(
        "mi_base",
        username="usuario",
        password="clave",
    )

    assert url.drivername == "postgresql+psycopg"
    assert url.username == "usuario"
    assert url.password == "clave"
    assert url.host == "servidor"
    assert url.port == 6543
    assert url.database == "mi_base"


def test_obtener_configuracion_desarrollo(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DB_NAME", "base_desarrollo")
    monkeypatch.setenv("DB_USER", "usuario_dev")
    monkeypatch.setenv("DB_PASSWORD", "clave_dev")

    configuracion = obtener_configuracion()

    assert configuracion is DevelopmentConfig
    assert configuracion.DATABASE_URL.database == "base_desarrollo"
    assert configuracion.DATABASE_URL.username == "usuario_dev"


def test_obtener_configuracion_testing(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.delenv("DB_TEST_NAME", raising=False)

    configuracion = obtener_configuracion()

    assert configuracion is TestingConfig
    assert configuracion.TESTING is True
    assert configuracion.DATABASE_URL.database == "proyecto_is1_2026_test"


def test_obtener_configuracion_produccion(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "clave-segura-produccion")
    monkeypatch.setenv("DB_PROD_NAME", "base_produccion")
    monkeypatch.setenv("DB_PROD_USER", "usuario_prod")
    monkeypatch.setenv("DB_PROD_PASSWORD", "clave_prod")
    monkeypatch.setenv("DB_HOST", "servidor-db")
    monkeypatch.setenv("DB_PORT", "5433")

    configuracion = obtener_configuracion()

    assert configuracion is ProductionConfig
    assert configuracion.DEBUG is False
    assert configuracion.TESTING is False
    assert configuracion.SECRET_KEY == "clave-segura-produccion"
    assert configuracion.DATABASE_URL.database == "base_produccion"
    assert configuracion.DATABASE_URL.username == "usuario_prod"
    assert configuracion.DATABASE_URL.password == "clave_prod"
    assert configuracion.DATABASE_URL.host == "servidor-db"
    assert configuracion.DATABASE_URL.port == 5433


@pytest.mark.parametrize(
    "variable",
    [
        "SECRET_KEY",
        "DB_PROD_NAME",
        "DB_PROD_USER",
        "DB_PROD_PASSWORD",
    ],
)
def test_produccion_requiere_variables_obligatorias(monkeypatch, variable):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "clave-segura")
    monkeypatch.setenv("DB_PROD_NAME", "base_produccion")
    monkeypatch.setenv("DB_PROD_USER", "usuario_prod")
    monkeypatch.setenv("DB_PROD_PASSWORD", "clave_prod")

    monkeypatch.delenv(variable)

    with pytest.raises(ValueError, match=variable):
        obtener_configuracion()


def test_produccion_rechaza_variables_vacias(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "   ")
    monkeypatch.setenv("DB_PROD_NAME", "base_produccion")
    monkeypatch.setenv("DB_PROD_USER", "usuario_prod")
    monkeypatch.setenv("DB_PROD_PASSWORD", "clave_prod")

    with pytest.raises(ValueError, match="SECRET_KEY"):
        obtener_configuracion()
