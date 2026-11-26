from types import SimpleNamespace

import pytest

from qanda.models import Pregunta
from qanda.services import (
    SRA,
    EstrategiaGeneracion,
    EstratGemini,
    EstratModLocal,
    EstratOpenAI,
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


def test_sra_rechaza_estrategias_invalidas():
    with pytest.raises(TypeError, match="EstrategiaGeneracion"):
        SRA(object())

    sra = SRA(EstratModLocal())

    with pytest.raises(TypeError, match="EstrategiaGeneracion"):
        sra.cambiar_estrategia(None)


def test_estrategia_generacion_es_abstracta():
    with pytest.raises(TypeError):
        EstrategiaGeneracion()

    with pytest.raises(NotImplementedError):
        EstrategiaGeneracion.generar(object(), crear_pregunta())


def test_openai_sin_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        EstratOpenAI()


def test_gemini_sin_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        EstratGemini()


def test_gemini_sin_texto():
    cliente = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: SimpleNamespace(text="")
        )
    )

    with pytest.raises(RuntimeError, match="no devolvió contenido"):
        EstratGemini(cliente=cliente).generar(crear_pregunta())
