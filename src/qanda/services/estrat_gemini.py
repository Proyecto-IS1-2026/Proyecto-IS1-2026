import os
from typing import Any

from qanda.models import Pregunta

from .estrategia_generacion import EstrategiaGeneracion


class EstratGemini(EstrategiaGeneracion):
    """Estrategia de generación que utiliza la API de Google Gemini."""

    def __init__(self, cliente: Any | None = None) -> None:
        # La inyección de cliente permite probar la estrategia sin llamar a la API.
        if cliente is None:
            try:
                from google import genai
            except ImportError as exc:
                raise RuntimeError(
                    "Falta instalar el SDK de Gemini. Ejecutá: uv add google-genai"
                ) from exc

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("No está definida la variable GEMINI_API_KEY.")

            cliente = genai.Client(api_key=api_key)

        self.cliente = cliente
        self.modelo = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    def generar(self, preg: Pregunta) -> str:
        prompt = (
            "Respondé la siguiente pregunta de un estudiante universitario "
            "de forma clara, precisa y didáctica.\n\n"
            f"Título: {preg.titulo}\n"
            f"Pregunta: {preg.cuerpo}"
        )

        respuesta = self.cliente.models.generate_content(
            model=self.modelo,
            contents=prompt,
        )

        if not respuesta.text:
            raise RuntimeError("Gemini no devolvió contenido de texto.")

        return respuesta.text
