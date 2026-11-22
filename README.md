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
