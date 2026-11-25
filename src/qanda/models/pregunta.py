import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .asociaciones import pregunta_etiqueta
from .base import Base

if TYPE_CHECKING:
    from .autor import Autor
    from .categoria import Categoria
    from .etiqueta import Etiqueta
    from .respuesta import Respuesta


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

    @classmethod
    def crear(cls, titulo, cuerpo, autor, categoria):

        if not titulo or not titulo.strip():
            raise ValueError("El título es obligatorio")

        if not cuerpo or not cuerpo.strip():
            raise ValueError("El cuerpo es obligatorio")

        if autor is None:
            raise ValueError("La pregunta debe tener un autor")

        if categoria is None:
            raise ValueError("La pregunta debe tener una categoría")

        return cls(
            titulo=titulo.strip(),
            cuerpo=cuerpo.strip(),
            autor=autor,
            categoria=categoria
        )

    def agregarEtiqueta(self, tag):

        if tag is None:
            raise ValueError("La etiqueta no puede ser nula")

        if tag not in self.etiquetas:
            self.etiquetas.append(tag)

    def quitarEtiqueta(self, tag):

        if tag in self.etiquetas:
            self.etiquetas.remove(tag)

    def aceptarRespuesta(self, respuesta, usuario):

        if usuario.id != self.autor_id:
            raise ValueError(
                "Solo el autor de la pregunta puede aceptar una respuesta"
            )

        if respuesta.pregunta_id != self.id:
            raise ValueError(
                "La respuesta no pertenece a esta pregunta"
            )

        for respuesta_anterior in self.respuestas:
            respuesta_anterior.aceptacion = False

        respuesta.aceptacion = True

    def tieneRespuestaAceptada(self):

        return any(
            respuesta.aceptacion
            for respuesta in self.respuestas
        )