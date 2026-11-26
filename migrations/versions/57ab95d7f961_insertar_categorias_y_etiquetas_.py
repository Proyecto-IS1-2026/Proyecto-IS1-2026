
"""insertar categorias y etiquetas iniciales

Revision ID: 57ab95d7f961
Revises: d571f6d0f4cb
Create Date: 2026-11-25
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "57ab95d7f961"
down_revision: str | Sequence[str] | None = "d571f6d0f4cb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


CATEGORIAS = [
    (
        uuid.UUID("a0000000-0000-4000-8000-000000000001"),
        "Python",
        "Preguntas sobre Python",
    ),
    (
        uuid.UUID("a0000000-0000-4000-8000-000000000002"),
        "SQL",
        "Preguntas sobre SQL",
    ),
    (
        uuid.UUID("a0000000-0000-4000-8000-000000000003"),
        "Flask",
        "Preguntas sobre Flask",
    ),
    (
        uuid.UUID("a0000000-0000-4000-8000-000000000004"),
        "PostgreSQL",
        "Preguntas sobre PostgreSQL",
    ),
    (
        uuid.UUID("a0000000-0000-4000-8000-000000000005"),
        "Otros",
        "Preguntas de otros temas",
    ),
    (
        uuid.UUID("a0000000-0000-4000-8000-000000000006"),
        "C",
        "Preguntas sobre lenguaje C",
    ),
]

ETIQUETAS = [
    (uuid.UUID("b0000000-0000-4000-8000-000000000001"), "Python"),
    (uuid.UUID("b0000000-0000-4000-8000-000000000002"), "SQL"),
    (uuid.UUID("b0000000-0000-4000-8000-000000000003"), "Flask"),
    (uuid.UUID("b0000000-0000-4000-8000-000000000004"), "PostgreSQL"),
    (uuid.UUID("b0000000-0000-4000-8000-000000000005"), "Otros"),
    (uuid.UUID("b0000000-0000-4000-8000-000000000006"), "C"),
    (uuid.UUID("b0000000-0000-4000-8000-000000000007"), "IA-help"),
]


def upgrade() -> None:
    """Inserta las categorias y etiquetas iniciales."""

    conexion = op.get_bind()

    categorias = sa.table(
        "categoria",
        sa.column("id", sa.Uuid()),
        sa.column("nombre", sa.String(100)),
        sa.column("descrip", sa.String(500)),
        schema="is1",
    )

    etiquetas = sa.table(
        "etiqueta",
        sa.column("id", sa.Uuid()),
        sa.column("nombre", sa.String(100)),
        schema="is1",
    )

    for identificador, nombre, descrip in CATEGORIAS:
        existe = conexion.execute(
            sa.select(categorias.c.id).where(
                categorias.c.nombre == nombre
            )
        ).first()

        if existe is None:
            conexion.execute(
                categorias.insert().values(
                    id=identificador,
                    nombre=nombre,
                    descrip=descrip,
                )
            )

    for identificador, nombre in ETIQUETAS:
        existe = conexion.execute(
            sa.select(etiquetas.c.id).where(
                etiquetas.c.nombre == nombre
            )
        ).first()

        if existe is None:
            conexion.execute(
                etiquetas.insert().values(
                    id=identificador,
                    nombre=nombre,
                )
            )


def downgrade() -> None:
    """Elimina exclusivamente los registros de esta migracion."""

    conexion = op.get_bind()

    categorias = sa.table(
        "categoria",
        sa.column("id", sa.Uuid()),
        schema="is1",
    )

    etiquetas = sa.table(
        "etiqueta",
        sa.column("id", sa.Uuid()),
        schema="is1",
    )

    ids_categorias = [identificador for identificador, _, _ in CATEGORIAS]
    ids_etiquetas = [identificador for identificador, _ in ETIQUETAS]

    conexion.execute(
        categorias.delete().where(
            categorias.c.id.in_(ids_categorias)
        )
    )

    conexion.execute(
        etiquetas.delete().where(
            etiquetas.c.id.in_(ids_etiquetas)
        )
    )
