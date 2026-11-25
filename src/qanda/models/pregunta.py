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


# Representa las preguntas publicadas por los usuarios del sistema.
class Pregunta(Base):
    __tablename__ = "pregunta"

    # Genera un identificador único a cada pregunta.
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    # Titulo de la pregunta que es obligatorio y admite hasta 255 caracteres.
    titulo: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Cuerpo de la pregunta que es obligatorio.
    cuerpo: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Fecha y hora de publicacion generada automaticamente por la base de datos.
    fecha_public: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Clave foranea que identifica al autor de la pregunta.
    autor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.autor.id"),
        nullable=False
    )

    # Clave foranea que identifica la categoria de la pregunta.
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.categoria.id"),
        nullable=False
    )

    # Relacion que permite acceder al autor de la pregunta.
    autor: Mapped["Autor"] = relationship()

    # Relacion con la categoria.
    # Desde una pregunta se puede acceder a su categoria y con back_populates
    # desde una categoria podemos acceder a todas sus preguntas.
    categoria: Mapped["Categoria"] = relationship(
        back_populates="preguntas"
    )

    # Relación de muchos a muchos con las etiquetas.
    # Usa una tabla intermedia para vincular preguntas y etiquetas.
    etiquetas: Mapped[list["Etiqueta"]] = relationship(
        secondary=pregunta_etiqueta,
        back_populates="preguntas"
    )

    # Relacion de uno a muchos con las respuestas.
    # Si se elimina una pregunta tambien se eliminan sus respuestas asociadas.
    respuestas: Mapped[list["Respuesta"]] = relationship(
        back_populates="pregunta",
        cascade="all, delete-orphan"
    )

    # Metodo que permite crear una pregunta y verifica que los datos sean correctos.
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

    # Agrega una etiqueta a la pregunta si todavia no tiene una.
    def agregarEtiqueta(self, tag):

        if tag is None:
            raise ValueError("La etiqueta no puede ser nula")

        if tag not in self.etiquetas:
            self.etiquetas.append(tag)

    # Elimina una etiqueta de la pregunta.
    def quitarEtiqueta(self, tag):

        if tag in self.etiquetas:
            self.etiquetas.remove(tag)

    # Permite al autor de la pregunta aceptar una de sus respuestas.
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

    # Comprueba si la pregunta ya tiene una respuesta aceptada.
    def tieneRespuestaAceptada(self):

        return any(
            respuesta.aceptacion
            for respuesta in self.respuestas
        )