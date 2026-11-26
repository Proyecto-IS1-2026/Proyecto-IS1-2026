# QandA — Proyecto IS1 2026

## 1. Información del proyecto

**Grupo:** Error_404

**Integrantes:**
- Cardozo, Ricardo Xavier
- Paglialunga, Julian
- Antonelli, Mariano
- Baumgartner, Federico Andrés
- Oviedo, Francisco Genaro

## 2. Descripción

QandA es una aplicación web desarrollada con Flask que permite gestionar preguntas y respuestas. Incluye funcionalidades de autenticación, publicación de preguntas, respuestas, administración y generación automática de respuestas mediante servicios de inteligencia artificial.

La aplicación está organizada en módulos para separar responsabilidades:

- **auth:** autenticación y gestión de sesiones de usuarios.
- **web:** vistas y funcionalidades principales de la aplicación.
- **admin:** funcionalidades de administración.
- **api:** endpoints para acceder a los recursos de la aplicación.
- **models:** modelos y relaciones de la base de datos.
- **services:** lógica de negocio y servicios auxiliares, incluyendo la generación automática de respuestas.

La persistencia de datos se implementa mediante PostgreSQL y SQLAlchemy. Las modificaciones del esquema de la base de datos se gestionan con Alembic.

## 3. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.12 | Lenguaje de programación |
| Flask | Framework web |
| Flask-Login | Autenticación y gestión de sesiones |
| SQLAlchemy | ORM y acceso a datos |
| PostgreSQL | Sistema de gestión de bases de datos |
| Alembic | Migraciones de base de datos |
| PyTorch | Aprendizaje automático |
| Scikit-Learn | Herramientas de aprendizaje automático |
| OpenAI / Gemini | Servicios de inteligencia artificial |
| Gunicorn | Servidor WSGI |
| Docker y Docker Compose | Contenedorización y ejecución de servicios |
| Pytest y pytest-cov | Pruebas automatizadas y cobertura |
| Ruff | Análisis estático y estilo de código |
| uv | Gestión de dependencias y entorno Python |

## 4. Requisitos previos

Para ejecutar el proyecto localmente se necesita:

- Python 3.12 o superior.
- [uv](https://docs.astral.sh/uv/).
- PostgreSQL 14 o superior.
- Git.

Para ejecutar el proyecto mediante Docker:

- Docker.
- Docker Compose.

## 5. Instalación y configuración local

### 5.1. Clonar el repositorio

Se puede clonar el repositorio utilizando cualquiera de estas dos alternativas.

**Opción 1: HTTPS**

```bash
git clone https://github.com/Proyecto-IS1-2026/Proyecto-IS1-2026.git
```

**Opción 2: SSH**

```bash
git clone git@github.com:Proyecto-IS1-2026/Proyecto-IS1-2026.git
```

La alternativa HTTPS permite clonar el repositorio sin configurar una clave SSH. Para utilizar SSH es necesario contar con una clave configurada y vinculada a la cuenta de GitHub.

Luego, ingresar al directorio del proyecto:

```bash
cd Proyecto-IS1-2026
```

### 5.2. Instalar las dependencias

El proyecto utiliza `uv` para administrar las dependencias y el entorno virtual.

```bash
uv sync --frozen
```

Este comando instala las dependencias definidas en `uv.lock`, incluyendo las dependencias de desarrollo.

### 5.3. Configurar PostgreSQL

Crear el usuario y las bases de datos necesarias para el entorno de desarrollo.

Se puede utilizar `psql` para ejecutar los siguientes comandos, reemplazando `TU_PASSWORD` por una contraseña propia:

```sql
CREATE USER is1_app WITH PASSWORD 'TU_PASSWORD';

CREATE DATABASE proyecto_is1_2026
    OWNER is1_app;

CREATE DATABASE proyecto_is1_2026_test
    OWNER is1_app;
```

Para ejecutar las pruebas automatizadas que utilizan bases de datos temporales, el usuario debe contar con el permiso `CREATEDB`:

```sql
ALTER USER is1_app CREATEDB;
```

### 5.4. Configurar las variables de entorno

Copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

Editar `.env` y completar los valores correspondientes al entorno local.

Las variables principales para el desarrollo son:

```dotenv
APP_ENV=development

SECRET_KEY=una_clave_secreta_local

DB_USER=is1_app
DB_PASSWORD=TU_PASSWORD
DB_HOST=localhost
DB_PORT=5432

DB_NAME=proyecto_is1_2026
DB_TEST_NAME=proyecto_is1_2026_test

ADMIN_NAME=Administrador
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=una_password_segura
```

La variable `SECRET_KEY` es recomendable en desarrollo y obligatoria en producción.

Las variables `ADMIN_NAME`, `ADMIN_EMAIL` y `ADMIN_PASSWORD` deben configurarse antes de ejecutar la migración encargada de crear el administrador inicial. La contraseña debe cumplir con la validación definida por el proyecto: al menos ocho caracteres.

Las variables de los proveedores de inteligencia artificial pueden configurarse si se desea utilizar esas funcionalidades.

**Importante:** los archivos `.env` y `.env.docker` contienen información de configuración y posibles credenciales. No deben subirse al repositorio ni compartirse públicamente.

### 5.5. Ejecutar las migraciones

Desde la raíz del proyecto, ejecutar:

```bash
uv run alembic upgrade head
```

Este comando aplica todas las migraciones pendientes y deja la base de datos en la última versión del esquema.

Las migraciones crean las tablas iniciales, insertan las categorías y etiquetas correspondientes y permiten crear el administrador inicial cuando se proporcionan las variables requeridas.

### 5.6. Iniciar la aplicación

Ejecutar:

```bash
uv run flask --app qanda run --debug
```

La aplicación estará disponible en:

[http://localhost:5000](http://localhost:5000)

## 6. Ejecución mediante Docker Compose

El proyecto permite ejecutar la aplicación y PostgreSQL mediante Docker Compose.

### 6.1. Configurar las variables de entorno

Copiar el archivo de ejemplo:

```bash
cp .env.docker.example .env.docker
```

Editar `.env.docker` y completar los valores requeridos:

```dotenv
APP_ENV=production

DB_PROD_NAME=proyecto_is1_2026_prod
DB_PROD_USER=is1_app
DB_PROD_PASSWORD=TU_PASSWORD

SECRET_KEY=una_clave_secreta_segura

ADMIN_NAME=Administrador
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=una_password_segura
```

La contraseña del administrador inicial debe cumplir con la validación definida por el proyecto: al menos ocho caracteres.

Las variables `OPENAI_API_KEY` y `GEMINI_API_KEY` pueden agregarse a `.env.docker` si se desea utilizar los servicios de inteligencia artificial correspondientes.

Las variables `OPENAI_MODEL` y `GEMINI_MODEL` permiten seleccionar los modelos durante la ejecución local. Sin embargo, la configuración actual de Docker Compose no transmite estas variables al servicio web. Por lo tanto, dentro del contenedor se utilizan los valores predeterminados definidos por cada estrategia:

- OpenAI: `gpt-5.5`.
- Gemini: `gemini-3.8-flash`.

Las claves API son opcionales para la ejecución general de la aplicación, pero necesarias cuando se utiliza la estrategia correspondiente.

### 6.2. Construir e iniciar los servicios

Ejecutar:

```bash
docker compose --env-file .env.docker up --build -d
```

Docker Compose inicia los siguientes servicios:

- **db:** instancia de PostgreSQL 15 Alpine.
- **web:** aplicación Flask ejecutada mediante Gunicorn.

El servicio web espera a que PostgreSQL se encuentre saludable antes de iniciar. Luego ejecuta las migraciones pendientes mediante Alembic y levanta Gunicorn con dos workers.

La aplicación estará disponible en:

[http://localhost:8000](http://localhost:8000)

### 6.3. Consultar el estado y los registros

Consultar el estado de los servicios:

```bash
docker compose --env-file .env.docker ps
```

Consultar los registros del servicio web:

```bash
docker compose --env-file .env.docker logs -f web
```

Para consultar los registros de PostgreSQL:

```bash
docker compose --env-file .env.docker logs -f db
```

### 6.4. Detener los servicios

Para detener los contenedores:

```bash
docker compose --env-file .env.docker down
```

Este comando detiene y elimina los contenedores, pero conserva el volumen `postgres_data` y la información almacenada en PostgreSQL.

**No utilizar `docker compose down -v` si se desea conservar los datos.**

## 7. Variables de entorno

Las variables de entorno permiten configurar el comportamiento de la aplicación según el entorno de ejecución.

### 7.1. Variables generales y de desarrollo

| Variable | Descripción |
|---|---|
| `APP_ENV` | Entorno de ejecución: `development`, `testing` o `production`. |
| `SECRET_KEY` | Clave secreta utilizada por Flask. Obligatoria en producción. |
| `DB_USER` | Usuario de PostgreSQL para desarrollo y testing. |
| `DB_PASSWORD` | Contraseña del usuario de PostgreSQL. |
| `DB_HOST` | Dirección del servidor PostgreSQL. |
| `DB_PORT` | Puerto de PostgreSQL. |
| `DB_NAME` | Nombre de la base de datos de desarrollo. |
| `DB_TEST_NAME` | Nombre de la base de datos de testing. |

### 7.2. Variables de producción y Docker

| Variable | Descripción |
|---|---|
| `DB_PROD_NAME` | Nombre de la base de datos de producción. |
| `DB_PROD_USER` | Usuario de PostgreSQL para producción. |
| `DB_PROD_PASSWORD` | Contraseña del usuario de producción. |

En Docker, las variables `DB_HOST` y `DB_PORT` se establecen automáticamente en `db` y `5432`, respectivamente.

### 7.3. Variables de testing

| Variable | Descripción |
|---|---|
| `TEST_DATABASE_URL` | URL de conexión a una base de mantenimiento de PostgreSQL utilizada por las pruebas automatizadas. |

Esta variable aparece comentada en `.env.example` porque solamente es necesaria cuando se ejecutan las pruebas que utilizan PostgreSQL.

El usuario de conexión debe tener permiso `CREATEDB`, ya que el mecanismo de testing crea y elimina bases de datos temporales.

### 7.4. Variables del administrador inicial

| Variable | Descripción |
|---|---|
| `ADMIN_NAME` | Nombre del administrador inicial. |
| `ADMIN_EMAIL` | Correo electrónico del administrador inicial. |
| `ADMIN_PASSWORD` | Contraseña del administrador inicial. |

Estas variables son utilizadas por la migración encargada de crear el administrador inicial.

### 7.5. Variables de inteligencia artificial

| Variable | Descripción |
|---|---|
| `OPENAI_API_KEY` | Clave de acceso al servicio de OpenAI. |
| `OPENAI_MODEL` | Modelo de OpenAI. Por defecto: `gpt-5.5`. |
| `GEMINI_API_KEY` | Clave de acceso al servicio de Gemini. |
| `GEMINI_MODEL` | Modelo de Gemini. Por defecto: `gemini-3.8-flash`. |

Las claves API son necesarias únicamente cuando se utiliza la estrategia correspondiente. Los nombres de los modelos son opcionales porque cada estrategia define un valor predeterminado.

En ejecución local, los modelos pueden seleccionarse mediante las variables `OPENAI_MODEL` y `GEMINI_MODEL`. En Docker Compose, estas variables no se transmiten actualmente al servicio web, por lo que se utilizan los valores predeterminados.

## 8. Pruebas automatizadas

El proyecto utiliza Pytest para ejecutar las pruebas automatizadas y pytest-cov para medir la cobertura del código.

### 8.1. Configurar la base de datos de testing

Las pruebas utilizan la variable `TEST_DATABASE_URL` para conectarse a una instancia de PostgreSQL con permisos suficientes para crear bases de datos temporales.

Ejemplo:

```dotenv
TEST_DATABASE_URL=postgresql+psycopg://is1_app:TU_PASSWORD@localhost:5432/postgres
```

La configuración de testing crea una base de datos temporal con un nombre único para las pruebas y la elimina al finalizar.

No es necesario cargar manualmente datos de prueba ni utilizar la base de datos de desarrollo.

### 8.2. Ejecutar todas las pruebas

```bash
uv run pytest
```

### 8.3. Ejecutar un archivo de pruebas específico

Por ejemplo:

```bash
uv run pytest tests/test_auth.py
```

### 8.4. Generar un informe HTML de cobertura

```bash
uv run pytest --cov-report=html
```

El informe se genera en el directorio `htmlcov/`.

## 9. Análisis estático

El proyecto utiliza Ruff para analizar el código y detectar problemas de estilo y calidad.

Ejecutar:

```bash
uv run ruff check .
```

## 10. Migraciones de base de datos

Las migraciones se gestionan mediante Alembic.

Para aplicar todas las migraciones pendientes:

```bash
uv run alembic upgrade head
```

Para consultar el historial:

```bash
uv run alembic history
```

Para consultar la revisión actual de la base de datos:

```bash
uv run alembic current
```

### Migraciones actuales

| Revisión | Descripción |
|---|---|
| `d571f6d0f4cb` | Creación de las tablas iniciales. |
| `57ab95d7f961` | Inserción de categorías y etiquetas iniciales. |
| `9e3b7c1a4d62` | Creación del administrador inicial. |

La migración del administrador utiliza las variables `ADMIN_NAME`, `ADMIN_EMAIL` y `ADMIN_PASSWORD`.

## 11. Integración continua (CI)

El proyecto utiliza GitHub Actions para ejecutar verificaciones automáticas ante cada `push` y `pull request`.

El workflow se encuentra en:

```text
.github/workflows/ci.yml
```

Actualmente contempla dos trabajos:

- **tests:** inicia un servicio PostgreSQL, instala las dependencias y ejecuta la suite de pruebas automatizadas.
- **ruff:** instala las dependencias y ejecuta el análisis estático del código.

Estas verificaciones permiten detectar errores y problemas de calidad antes de integrar cambios a las ramas principales del proyecto.

## 12. Documentación adicional

La documentación correspondiente al Sistema de Respuestas Automáticas (SRA) se encuentra en:

```text
README_SRA.md
```

Allí se describen los aspectos específicos de ese componente del proyecto.
