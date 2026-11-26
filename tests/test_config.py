import pytest

from qanda.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    crear_database_url,
    obtener_configuracion,
    obtener_variable_obligatoria,
)


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


def test_configuracion_produccion_requiere_secret_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(ValueError, match="SECRET_KEY"):
        obtener_configuracion()


def test_configuracion_produccion(monkeypatch):
    secret_original = ProductionConfig.SECRET_KEY
    url_original = getattr(ProductionConfig, "DATABASE_URL", None)

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "clave-produccion")
    monkeypatch.setenv("DB_PROD_NAME", "base_produccion")
    monkeypatch.setenv("DB_PROD_USER", "usuario_prod")
    monkeypatch.setenv("DB_PROD_PASSWORD", "clave_prod")

    try:
        configuracion = obtener_configuracion()

        assert configuracion is ProductionConfig
        assert configuracion.SECRET_KEY == "clave-produccion"
        assert configuracion.DATABASE_URL.database == "base_produccion"
        assert configuracion.DATABASE_URL.username == "usuario_prod"

    finally:
        ProductionConfig.SECRET_KEY = secret_original

        if url_original is None:
            if hasattr(ProductionConfig, "DATABASE_URL"):
                delattr(ProductionConfig, "DATABASE_URL")
        else:
            ProductionConfig.DATABASE_URL = url_original
