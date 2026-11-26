import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .pregunta import Pregunta


# Representa las categorias que permiten organizar las preguntas.
class Categoria(Base):
    __tablename__ = "categoria"

    # Genera un identificador unico de la categoria.
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Nombre de la categoria que es obligatorio.
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    # Descripcion de la categoria que es obligatoria.
    descrip: Mapped[str] = mapped_column(String(500), nullable=False)

    # Relación con pregunta, desde una categoria se puede acceder a todas
    # sus preguntas y con back_populates desde una pregunta
    # podemos acceder a la categoria a la que pertenece.
    preguntas: Mapped[list["Pregunta"]] = relationship(back_populates="categoria")
