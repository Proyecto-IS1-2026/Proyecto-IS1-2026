from types import SimpleNamespace

import pytest

from qanda.models import Pregunta
from qanda.services import (
    EstratGemini,
    EstratModLocal,
    EstratOpenAI,
    EstrategiaGeneracion,
    SRA,
)


def crear_pregunta():
    return Pregunta(
        titulo="¿Qué es Python?",
        cuerpo="¿Cuáles son sus principales características?",
    )


def test_sra_delega_en_la_estrategia():
    class EstrategiaPrueba(EstrategiaGeneracion):
        def generar(self, preg):
            return f"Respuesta a: {preg.titulo}"

    sra = SRA(EstrategiaPrueba())

    assert sra.generar(crear_pregunta()) == "Respuesta a: ¿Qué es Python?"


def test_sra_permite_cambiar_estrategia():
    class EstrategiaA(EstrategiaGeneracion):
        def generar(self, preg):
            return "A"

    class EstrategiaB(EstrategiaGeneracion):
        def generar(self, preg):
            return "B"

    sra = SRA(EstrategiaA())
    assert sra.generar(crear_pregunta()) == "A"

    sra.cambiar_estrategia(EstrategiaB())
    assert sra.generar(crear_pregunta()) == "B"


def test_openai_usa_el_cliente_y_devuelve_el_texto():
    cliente = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(output_text="Respuesta OpenAI")
        )
    )
    estrategia = EstratOpenAI(cliente=cliente)

    assert estrategia.generar(crear_pregunta()) == "Respuesta OpenAI"


def test_gemini_usa_el_cliente_y_devuelve_el_texto():
    cliente = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: SimpleNamespace(text="Respuesta Gemini")
        )
    )
    estrategia = EstratGemini(cliente=cliente)

    assert estrategia.generar(crear_pregunta()) == "Respuesta Gemini"


def test_modelo_local_es_placeholder():
    with pytest.raises(NotImplementedError, match="todavía no está implementada"):
        EstratModLocal().generar(crear_pregunta())
