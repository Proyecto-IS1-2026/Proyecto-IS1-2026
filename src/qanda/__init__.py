from flask import Flask
from qanda.config import Config
from qanda.extensions import init_db

from qanda.api import api_bp
from qanda.api import health  # noqa: F401
from qanda.web import web_bp
from qanda.web import main  # noqa: F401


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    return app
