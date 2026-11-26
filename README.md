# Proyecto-IS1-2026

## Nombre del grupo: Error_404

## Integrantes

- Cardozo Ricardo Xavier
- Paglialunga Julian
- Antonelli Mariano
- Baumgartner Federico Andrés
- Oviedo Francisco Genaro

## Tecnologías utilizadas

- Python 3.12
- Flask
- PostgreSQL
- SQLAlchemy
- Alembic
- Gunicorn
- Docker y Docker Compose
- Pytest
- Ruff

## Configuración de la base de datos

El proyecto utiliza PostgreSQL como motor de base de datos, SQLAlchemy para la interacción con los datos y Alembic para administrar las migraciones.

Para aplicar las migraciones pendientes:

```bash
uv run alembic upgrade head
```

Para consultar la revisión actualmente aplicada:

```bash
uv run alembic current
```

Para consultar las migraciones disponibles:

```bash
uv run alembic heads
```

Los archivos SQL complementarios se encuentran en el directorio `baseDeDatos`.

## Pruebas y calidad

Las pruebas utilizan una base de datos PostgreSQL descartable: se crea una base nueva con un nombre único, se genera el esquema `is1` desde los modelos y se elimina al finalizar.

No hace falta cargar datos de ejemplo ni configurar `.env`.

Antes de ejecutar las pruebas, definir `TEST_DATABASE_URL` apuntando a una base de mantenimiento cuyo usuario tenga permisos para crear bases de datos.

**Linux:**

```bash
export TEST_DATABASE_URL="postgresql+psycopg://usuario:password@localhost:5432/postgres"
uv run pytest
```

**Windows PowerShell:**

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://usuario:password@localhost:5432/postgres"
uv run pytest
```

Comandos habituales:

```bash
uv run pytest                          # Ejecutar pruebas con cobertura
uv run pytest --cov-report=html        # Generar reporte HTML en htmlcov/
uv run ruff check .                    # Verificar calidad del código
```

La cobertura se informa, pero no hace fallar la suite: no hay un valor `fail_under` configurado.

## Despliegue local con Docker

El proyecto incluye Docker Compose para ejecutar la aplicación Flask y PostgreSQL en contenedores.

### Requisitos

- Docker Engine
- Docker Compose

### 1. Configurar las variables de entorno

Crear el archivo de configuración local a partir del ejemplo:

```bash
cp .env.docker.example .env.docker
```

Editar `.env.docker` y reemplazar los valores de ejemplo por credenciales seguras.

Este archivo contiene información sensible y no debe subirse al repositorio.

### 2. Construir e iniciar los servicios

Desde la raíz del proyecto:

```bash
docker compose --env-file .env.docker up -d --build
```

Docker Compose inicia los siguientes servicios:

- **db:** servidor PostgreSQL 15.
- **web:** aplicación Flask ejecutada mediante Gunicorn.

La aplicación espera a que PostgreSQL esté disponible antes de iniciar. Luego ejecuta automáticamente las migraciones pendientes con Alembic y levanta Gunicorn.

### 3. Verificar el despliegue

Consultar el estado de los contenedores:

```bash
docker compose --env-file .env.docker ps
```

Consultar los registros de la aplicación:

```bash
docker compose --env-file .env.docker logs web
```

Consultar los registros de todos los servicios:

```bash
docker compose --env-file .env.docker logs
```

Comprobar que la aplicación responde:

```bash
curl -i http://localhost:8000/
```

La aplicación queda disponible en:

http://localhost:8000/

Una respuesta HTTP `200 OK` indica que la página principal está respondiendo correctamente.

### 4. Detener los servicios

Para detener y eliminar los contenedores y la red:

```bash
docker compose --env-file .env.docker down
```

Los datos de PostgreSQL se conservan en un volumen persistente, por lo que detener los servicios de esta manera no elimina la información almacenada.

Para volver a iniciar los servicios:

```bash
docker compose --env-file .env.docker up -d
```

### 5. Reconstruir la aplicación

Si se realizan cambios en el código o en el Dockerfile, reconstruir y levantar los servicios con:

```bash
docker compose --env-file .env.docker up -d --build
```

## Integración continua

El proyecto cuenta con un flujo de integración continua mediante GitHub Actions.

El flujo se ejecuta ante eventos de `push` y `pull_request`, y realiza verificaciones de calidad y pruebas automatizadas utilizando PostgreSQL.
