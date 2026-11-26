import uuid
from typing import ClassVar

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .autor import Autor


class AgenteIA(Autor):
    __tablename__ = "agente_ia"

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("is1.autor.id"), primary_key=True)

    __mapper_args__: ClassVar[dict[str, object]] = {"polymorphic_identity": "agente_ia"}
