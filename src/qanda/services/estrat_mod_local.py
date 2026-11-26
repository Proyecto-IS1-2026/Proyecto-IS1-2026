from qanda.models import Pregunta

from .estrategia_generacion import EstrategiaGeneracion


class EstratModLocal(EstrategiaGeneracion):
    """Placeholder para una futura integración con un modelo local."""

    def generar(self, preg: Pregunta) -> str:
        raise NotImplementedError(
            "La estrategia de modelo local todavía no está implementada."
        )
