
"""Endpoints de estado y disponibilidad de la API."""

from flask import jsonify

from qanda.api import api_bp


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Informa si la API está respondiendo correctamente."""
    return jsonify({"status": "ok", "message": "QandA API is running"}), 200
