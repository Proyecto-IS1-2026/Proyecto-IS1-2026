from sqlalchemy import select

from qanda.models import AgenteIA, Pregunta, Respuesta

from .estrat_gemini import EstratGemini
from .estrat_openai import EstratOpenAI
from .estrategia_generacion import EstrategiaGeneracion


class SRA:
    """Servicio de Respuestas Automáticas (Contexto del patrón Strategy)."""

    def __init__(self, estrategia: EstrategiaGeneracion) -> None:
        self.cambiar_estrategia(estrategia)

    def cambiar_estrategia(self, estrategia: EstrategiaGeneracion) -> None:
        """Permite seleccionar otra estrategia de generación."""
        if not isinstance(estrategia, EstrategiaGeneracion):
            raise TypeError("La estrategia debe implementar EstrategiaGeneracion.")

        self.estrategia = estrategia

    def generar(self, preg: Pregunta) -> str:
        """Delega la generación de la respuesta en la estrategia actual."""
        return self.estrategia.generar(preg)


def generar_respuesta_ia(session, pregunta, proveedor):
    """Genera una respuesta automática y la asocia a un agente de IA."""

    if proveedor == "openai":
        estrategia = EstratOpenAI()
        nombre_agente = "ChatGPT"

    elif proveedor == "gemini":
        estrategia = EstratGemini()
        nombre_agente = "Gemini"

    else:
        raise ValueError("Proveedor de IA no válido.")

    servicio = SRA(estrategia)
    contenido = servicio.generar(pregunta)

    if not contenido or not contenido.strip():
        raise ValueError("La IA no generó una respuesta.")

    agente = session.scalar(
        select(AgenteIA).where(
            AgenteIA.nombre == nombre_agente
        )
    )

    if agente is None:
        agente = AgenteIA(nombre=nombre_agente)
        session.add(agente)
        session.flush()

    respuesta = Respuesta(
        cuerpo=contenido,
        pregunta=pregunta,
        autor=agente,
    )

    session.add(respuesta)

    return respuesta


class SRA:
    def __init__(self, estrategia: EstrategiaGeneracion):
        self.cambiar_estrategia(estrategia)

    def cambiar_estrategia(self, estrategia: EstrategiaGeneracion):
        if not isinstance(estrategia, EstrategiaGeneracion):
            raise TypeError(
                "La estrategia debe ser una instancia de EstrategiaGeneracion"
            )

        self.estrategia = estrategia

    def generar(self, pregunta):
        return self.estrategia.generar(pregunta)
