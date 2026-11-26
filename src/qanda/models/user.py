
import uuid
from typing import ClassVar

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from .autor import Autor


class Usuario(Autor, UserMixin):
    __tablename__ = "usuario"

    # Restriccion que limita los roles permitidos a ADMIN y GENERAL.
    __table_args__ = (
        CheckConstraint(
            "rol IN ('ADMIN', 'GENERAL')",
            name="ck_usuario_rol",
        ),
    )

    # Clave primaria que tambien es clave foranea de la tabla Autor.
    # Permite implementar la herencia entre ambas tablas.
    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("is1.autor.id"),
        primary_key=True,
    )

    # Correo electronico unico y obligatorio para cada usuario.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    # Almacena el hash de la contraseña.
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Define el rol del usuario que por defecto es GENERAL.
    rol: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="GENERAL",
    )

    __mapper_args__: ClassVar[dict[str, object]] = {
        "polymorphic_identity": "usuario",
    }

    # Registra los datos del usuario y verifica que sean correctos.
    def registrarse(self, nombre, email, password):
        if not nombre or not email or not password:
            raise ValueError("Todos los campos son obligatorios")

        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")

        email = email.strip().lower()

        if "@" not in email:
            raise ValueError("El email no tiene un formato válido")

        self.nombre = nombre.strip()
        self.email = email
        self.password_hash = generate_password_hash(password)

        if not self.rol:
            self.rol = "GENERAL"

    # Verifica si la contraseña ingresada coincide con el hash almacenado.
    def autenticarse(self, password):
        if not password:
            raise ValueError("La contraseña es obligatoria")

        if not check_password_hash(self.password_hash, password):
            raise ValueError("La contraseña es incorrecta")

        return True

    # Permite que el usuario cree una pregunta.
    def realizarPregunta(self, titulo, cuerpo, categoria):
        from .pregunta import Pregunta

        if not titulo or not cuerpo:
            raise ValueError("El título y el cuerpo son obligatorios")

        if categoria is None:
            raise ValueError("La pregunta debe tener una categoría")

        return Pregunta(
            titulo=titulo,
            cuerpo=cuerpo,
            autor=self,
            categoria=categoria,
        )
