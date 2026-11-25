import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .autor import Autor
    from .pregunta import Pregunta


# Representa las respuestas que los usuarios realizan a las preguntas.
class Respuesta(Base):
    __tablename__ = "respuesta"

    # Genera un identificador unico a cada respuesta.
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Cuerpo de la respuesta que es obligatorio.
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)

    # Fecha y hora de publicacion generada automaticamente por la base de datos.
    fecha_public: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Indica si la respuesta fue aceptada por el autor de la pregunta.
    aceptacion: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    # Clave foranea que identifica la pregunta a la que pertenece la respuesta.
    # Si se elimina la pregunta tambien se eliminan sus respuestas asociadas.
    pregunta_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.pregunta.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Clave foranea que identifica al autor que realizo la respuesta.
    autor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.autor.id"),
        nullable=False,
    )

    # Relacion con pregunta, desde la respuesta se puede acceder a la pregunta
    # a la que pertenece y con back_populates desde una pregunta
    # podemos acceder a todas sus respuestas.
    pregunta: Mapped["Pregunta"] = relationship(back_populates="respuestas")

    # Permite acceder al autor que realizó la respuesta.
    autor: Mapped["Autor"] = relationship()
