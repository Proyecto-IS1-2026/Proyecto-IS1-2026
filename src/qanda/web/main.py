from flask import render_template

from qanda.web import web_bp


@web_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")
