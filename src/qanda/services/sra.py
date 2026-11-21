from qanda.models import Pregunta

from .estrategia_generacion import EstrategiaGeneracion


class SRA:
    """Servicio de Respuestas Automáticas (Context de Strategy)."""

    def __init__(self, estrategia: EstrategiaGeneracion) -> None:
        self.cambiar_estrategia(estrategia)

    def cambiar_estrategia(self, estrategia: EstrategiaGeneracion) -> None:
        if not isinstance(estrategia, EstrategiaGeneracion):
            raise TypeError("La estrategia debe implementar EstrategiaGeneracion.")
        self.estrategia = estrategia

    def generar(self, preg: Pregunta) -> str:
        return self.estrategia.generar(preg)
