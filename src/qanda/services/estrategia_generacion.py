from abc import ABC, abstractmethod

from qanda.models import Pregunta


class EstrategiaGeneracion(ABC):
    """Interfaz de las estrategias para generar respuestas automáticas."""

    @abstractmethod
    def generar(self, preg: Pregunta) -> str:
        """Genera el texto de una respuesta a partir de una pregunta."""
        raise NotImplementedError
