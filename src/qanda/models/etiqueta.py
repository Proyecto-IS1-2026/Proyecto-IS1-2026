import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .asociaciones import pregunta_etiqueta
from .base import Base

if TYPE_CHECKING:
    from .pregunta import Pregunta


# Representa las etiquetas que permiten clasificar las preguntas.
class Etiqueta(Base):
    __tablename__ = "etiqueta"

    # Genera un identificador unico de la etiqueta.
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Nombre de la etiqueta que es obligatorio.
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relacion con pregunta, desde una etiqueta se puede acceder a todas
    # las preguntas asociadas y con back_populates desde una pregunta
    # podemos acceder a todas sus etiquetas.
    preguntas: Mapped[list["Pregunta"]] = relationship(
        secondary=pregunta_etiqueta,
        back_populates="etiquetas",
    )
