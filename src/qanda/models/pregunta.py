import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .asociaciones import pregunta_etiqueta
from .base import Base


class Pregunta(Base):
    __tablename__ = "pregunta"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    titulo: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    cuerpo: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    fecha_public: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    autor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.autor.id"),
        nullable=False
    )

    categoria_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.categoria.id"),
        nullable=False
    )

    autor: Mapped["Autor"] = relationship()

    categoria: Mapped["Categoria"] = relationship(
        back_populates="preguntas"
    )

    etiquetas: Mapped[list["Etiqueta"]] = relationship(
        secondary=pregunta_etiqueta,
        back_populates="preguntas"
    )

    respuestas: Mapped[list["Respuesta"]] = relationship(
        back_populates="pregunta",
        cascade="all, delete-orphan"
    )

    def agregarEtiqueta(self, tag):

        if tag not in self.etiquetas:
            self.etiquetas.append(tag)

    def aceptarRespuesta(self, respuesta, usuario):

        # Comprueba que el usuario sea el autor de la pregunta
        if usuario.id != self.autor_id:
            raise ValueError(
                "Solo el autor de la pregunta puede aceptar una respuesta"
            )

        # Comprueba que la respuesta pertenezca a esta pregunta
        if respuesta.pregunta is not self:
            raise ValueError(
                "La respuesta no pertenece a esta pregunta"
            )

        # Desmarcar cualquier respuesta aceptada anteriormente
        for respuesta_anterior in self.respuestas:
            respuesta_anterior.aceptacion = False

        respuesta.aceptacion = True