from sqlalchemy import Column, ForeignKey, Table, Uuid

from .base import Base


pregunta_etiqueta = Table(
    "pregunta_etiqueta",
    Base.metadata,
    Column(
        "pregunta_id",
        Uuid(as_uuid=True),
        ForeignKey("is1.pregunta.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "etiqueta_id",
        Uuid(as_uuid=True),
        ForeignKey("is1.etiqueta.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
