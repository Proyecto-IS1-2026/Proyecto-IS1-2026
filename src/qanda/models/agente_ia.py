
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .autor import Autor


class AgenteIA(Autor):
    __tablename__ = "agente_ia"

    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.autor.id"),
        primary_key=True
    )

    __mapper_args__ = {
        "polymorphic_identity": "agente_ia"
    }

