
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .autor import Autor


class Usuario(Autor):
    __tablename__ = "usuario"

    __table_args__ = (
        CheckConstraint(
            "rol IN ('ADMIN', 'GENERAL')",
            name="ck_usuario_rol"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.autor.id"),
        primary_key=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    rol: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="GENERAL"
    )

    __mapper_args__ = {
        "polymorphic_identity": "usuario"
    }


