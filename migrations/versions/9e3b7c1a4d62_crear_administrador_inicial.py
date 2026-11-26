import os
import uuid

import sqlalchemy as sa
from alembic import op
from werkzeug.security import generate_password_hash

revision = "9e3b7c1a4d62"
down_revision = "57ab95d7f961"
branch_labels = None
depends_on = None


ADMIN_ID = uuid.UUID("f6a8b2c1-7d34-4e90-a621-5c9f3b8d2e10")


def upgrade():
    nombre = os.getenv("ADMIN_NAME", "").strip()
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")

    if not nombre:
        raise RuntimeError("Falta configurar ADMIN_NAME.")

    if len(nombre) > 100:
        raise RuntimeError("ADMIN_NAME no puede superar los 100 caracteres.")

    if not email:
        raise RuntimeError("Falta configurar ADMIN_EMAIL.")

    if len(email) > 255:
        raise RuntimeError("ADMIN_EMAIL no puede superar los 255 caracteres.")

    if not password or len(password) < 8:
        raise RuntimeError(
            "ADMIN_PASSWORD es obligatorio y debe tener al menos "
            "8 caracteres."
        )

    conexion = op.get_bind()

    autor = sa.table(
        "autor",
        sa.column("id", sa.Uuid()),
        sa.column("nombre", sa.String(100)),
        sa.column("tipo", sa.String(20)),
        schema="is1",
    )

    usuario = sa.table(
        "usuario",
        sa.column("id", sa.Uuid()),
        sa.column("email", sa.String(255)),
        sa.column("password_hash", sa.String(255)),
        sa.column("rol", sa.String(10)),
        schema="is1",
    )

    usuario_existente = conexion.execute(
        sa.select(usuario.c.id).where(usuario.c.email == email)
    ).first()

    if usuario_existente is not None:
        raise RuntimeError(
            "ADMIN_EMAIL ya pertenece a un usuario existente. "
            "Elegí otro email para el administrador inicial."
        )

    autor_existente = conexion.execute(
        sa.select(autor.c.id).where(autor.c.id == ADMIN_ID)
    ).first()

    if autor_existente is not None:
        raise RuntimeError(
            "El UUID reservado para el administrador inicial ya existe."
        )

    conexion.execute(
        autor.insert().values(
            id=ADMIN_ID,
            nombre=nombre,
            tipo="usuario",
        )
    )

    conexion.execute(
        usuario.insert().values(
            id=ADMIN_ID,
            email=email,
            password_hash=generate_password_hash(password),
            rol="ADMIN",
        )
    )


def downgrade():
    conexion = op.get_bind()

    usuario = sa.table(
        "usuario",
        sa.column("id", sa.Uuid()),
        schema="is1",
    )

    autor = sa.table(
        "autor",
        sa.column("id", sa.Uuid()),
        schema="is1",
    )

    conexion.execute(
        usuario.delete().where(usuario.c.id == ADMIN_ID)
    )

    conexion.execute(
        autor.delete().where(autor.c.id == ADMIN_ID)
    )
