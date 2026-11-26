"""Inicialización de la aplicación Flask mediante Application Factory."""

import logging

from flask import Flask

from qanda.admin import admin_bp
from qanda.api import (
    api_bp,
    health,  # noqa: F401
    preguntas,  # noqa: F401
)
from qanda.api import (
    respuestas as respuestas,
)
from qanda.auth import auth_bp
from qanda.config import obtener_configuracion
from qanda.extensions import init_db, init_login
from qanda.web import (
    main,  # noqa: F401
    web_bp,
)


def create_app(config_class=None):
    """Crea y configura una instancia de la aplicación Flask.

    Permite seleccionar una configuración explícita o determinarla
    automáticamente según la variable de entorno APP_ENV.
    """
    app = Flask(__name__)

    if config_class is None:
        config_class = obtener_configuracion()

    app.config.from_object(config_class)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Iniciando aplicacion QandA")

    # Inicializa las extensiones antes de registrar las rutas.
    init_db(app)
    init_login(app)

    # Cada blueprint agrupa las rutas de un módulo funcional.
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def utilidades_template():
        """Proporciona utilidades compartidas por las plantillas."""
        return {
            "endpoint_existe": lambda nombre: nombre in app.view_functions
        }

    app.logger.info("Aplicacion QandA inicializada correctamente")

    return app
