import os
from typing import Any

from qanda.models import Pregunta

from .estrategia_generacion import EstrategiaGeneracion


class EstratOpenAI(EstrategiaGeneracion):
    """Estrategia de generación que utiliza la API de OpenAI."""

    def __init__(self, cliente: Any | None = None) -> None:
        # La inyección de cliente permite probar la estrategia sin llamar a la API.
        if cliente is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "Falta instalar el SDK de OpenAI. Ejecutá: uv add openai"
                ) from exc

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("No está definida la variable OPENAI_API_KEY.")

            cliente = OpenAI(api_key=api_key)

        self.cliente = cliente
        self.modelo = os.getenv("OPENAI_MODEL", "gpt-5.5")

    def generar(self, preg: Pregunta) -> str:
        prompt = (
            "Respondé la siguiente pregunta de un estudiante universitario "
            "de forma clara, precisa y didáctica.\n\n"
            f"Título: {preg.titulo}\n"
            f"Pregunta: {preg.cuerpo}"
        )

        respuesta = self.cliente.responses.create(
            model=self.modelo,
            input=prompt,
        )

        return respuesta.output_text
