from flask import Flask

from qanda.api import (
    api_bp,
    health,  # noqa: F401
)
from qanda.config import Config
from qanda.extensions import init_db
from qanda.web import (
    main,  # noqa: F401
    web_bp,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    return app
