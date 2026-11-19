import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .asociaciones import pregunta_etiqueta
from .base import Base


class Etiqueta(Base):
    __tablename__ = "etiqueta"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    nombre: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    preguntas: Mapped[list["Pregunta"]] = relationship(
        secondary=pregunta_etiqueta,
        back_populates="etiquetas",
    )
