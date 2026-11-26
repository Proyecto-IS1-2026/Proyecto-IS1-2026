
from sqlalchemy import select

from qanda.models import AgenteIA, Respuesta

from .estrat_openai import EstratOpenAI
from .estrat_gemini import EstratGemini


def generar_respuesta_ia(session, pregunta, proveedor):

    if proveedor == "openai":
        estrategia = EstratOpenAI()
        nombre_agente = "ChatGPT"

    elif proveedor == "gemini":
        estrategia = EstratGemini()
        nombre_agente = "Gemini"

    else:
        raise ValueError("Proveedor de IA no válido.")

    contenido = estrategia.generar(pregunta)

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
