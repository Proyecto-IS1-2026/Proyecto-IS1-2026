import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .pregunta import Pregunta


class Categoria(Base):
    __tablename__ = "categoria"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    descrip: Mapped[str] = mapped_column(String(500), nullable=False)

    preguntas: Mapped[list["Pregunta"]] = relationship(back_populates="categoria")
