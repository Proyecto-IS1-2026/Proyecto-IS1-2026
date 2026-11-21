import uuid
from typing import ClassVar
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .autor import Autor


class Usuario(Autor):
    __tablename__ = "usuario"

    # Un usuario solo puede ser ADMIN o GENERAL
    __table_args__ = (
        CheckConstraint("rol IN ('ADMIN', 'GENERAL')", name="ck_usuario_rol"),
    )

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("is1.autor.id"), primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Registra los datos del usuario
    def registrarse(self, nombre, email, password):

        if not nombre or not email or not password:
            raise ValueError(
                "Todos los campos son obligatorios"
            )

        if len(password) < 8:
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres"
            )

        email = email.strip().lower()

        if "@" not in email:
            raise ValueError(
                "El email no tiene un formato válido"
            )

        self.nombre = nombre.strip()
        self.email = email
        # Transforma la contraseña en un hash seguro de almacenar
        self.password_hash = generate_password_hash(password)

        if not self.rol:
            self.rol = "GENERAL"

    # Verifica si la contraseña coincide con la almacenada
    def autenticarse(self, password):

        if not password:
            raise ValueError(
                "La contraseña es obligatoria"
            )

        if not check_password_hash(
            self.password_hash,
            password
        ):
            raise ValueError(
                "La contraseña es incorrecta"
            )

        return True

    # Permite al usuario crear una pregunta
    def realizarPregunta(self, titulo, cuerpo, categoria):

        from .pregunta import Pregunta

        if not titulo or not cuerpo:
            raise ValueError(
                "El título y el cuerpo son obligatorios"
            )

        if categoria is None:
            raise ValueError(
                "La pregunta debe tener una categoría"
            )

        pregunta = Pregunta(
            titulo=titulo,
            cuerpo=cuerpo,
            autor=self,
            categoria=categoria
        )

        # Devuelve un objeto tipo pregunta
        return pregunta
