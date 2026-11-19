import uuid
from datetime import datetime

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


class Respuesta(Base):
    __tablename__ = "respuesta"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    cuerpo: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    fecha_public: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    aceptacion: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    pregunta_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.pregunta.id", ondelete="CASCADE"),
        nullable=False,
    )

    autor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.autor.id"),
        nullable=False,
    )

    pregunta: Mapped["Pregunta"] = relationship(
        back_populates="respuestas"
    )

    autor: Mapped["Autor"] = relationship()
