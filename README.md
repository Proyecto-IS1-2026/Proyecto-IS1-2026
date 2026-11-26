# Proyecto-IS1-2026

## Nombre del grupo: Error_404

## Integrantes:

- Cardozo Ricardo Xavier
- Paglialunga Julian
- Antonelli Mariano
- Baumgartner Federico Andrés
- Oviedo Francisco Genaro

## Configuracion de la Base De Datos

Este proyecto usa como motor de base de datos PostgreSQL, en conjunto con SQLAlchemy y Alembic para las migraciones.

\*El esquema debe ser ejecutado, en el archivo baseDeDatos se encuentran los archivos .sql.

\*En la ubicacion donde esta el proyecto /Proyecto-IS1-2026$ ejecutar uv run alembic -c migrations/alembic.ini current para comprobar la conexion

\*Para ejecutar las pruebas uv run pytest -q tests/test_database.py

## Pruebas y calidad

Las pruebas usan una base PostgreSQL descartable: se crea una base nueva con
un nombre único, se genera el esquema `is1` desde los modelos y se elimina al
finalizar. No hace falta cargar datos de ejemplo ni configurar `.env`.

Antes de ejecutarlas, definir `TEST_DATABASE_URL` apuntando a una base de
mantenimiento cuyo usuario pueda crear bases de datos:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://usuario:password@localhost:5432/postgres"
uv run pytest
```

```bash
export TEST_DATABASE_URL="postgresql+psycopg://usuario:password@localhost:5432/postgres"
uv run pytest
```

Comandos habituales:

```bash
uv run pytest                          # con reporte de cobertura
uv run pytest --cov-report=html        # reporte HTML en htmlcov/
uv run ruff check .                    # lint sobre todo el proyecto
```

La cobertura se informa pero no hace fallar la suite: no hay `fail_under`
configurado.
