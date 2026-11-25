import uuid
from typing import ClassVar

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


# Representa la entidad base de los autores del sistema.
# Sirve como clase padre para otros modelos que comparten sus atributos.
class Autor(Base):
    __tablename__ = "autor"

    # Genera un identificador unico del autor.
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Nombre del autor que es obligatorio.
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    # Indica el tipo de autor y permite identificar a qué subclase pertenece.
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    # Configuración de la herencia polimórfica:
    # polymorphic_on indica que se usa el campo tipo para identificar
    # la clase correspondiente a cada registro.
    # polymorphic_abstract indica que autor es una clase base abstracta.
    __mapper_args__: ClassVar[dict[str, object]] = {
        "polymorphic_on": tipo,
        "polymorphic_abstract": True,
    }
