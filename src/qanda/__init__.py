from flask import Flask

from qanda.api import api_bp
from qanda.api import health  # noqa: F401


def create_app():
    app = Flask(__name__)

    app.register_blueprint(api_bp)

    return app
