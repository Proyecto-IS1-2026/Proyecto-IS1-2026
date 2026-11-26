# Proyecto-IS1-2026

## Nombre del grupo: Error_404

## Integrantes

- Cardozo Ricardo Xavier
- Paglialunga Julian
- Antonelli Mariano
- Baumgartner Federico Andrés
- Oviedo Francisco Genaro

## Descripción

QandA es una aplicación Flask con preguntas, respuestas, moderación y generación
de respuestas automáticas. El código fuente está en `src/qanda` y se organiza en
estos módulos:

- `auth`: registro, inicio de sesión y cierre de sesión.
- `web`: listado de preguntas, creación de preguntas, respuestas y aceptación.
- `admin`: moderación de preguntas y respuestas.
- `api`: endpoints JSON para preguntas, respuestas y healthcheck.
- `services`: estrategias del Servicio de Respuestas Automáticas (SRA).

La persistencia usa PostgreSQL + SQLAlchemy, y los cambios de esquema se gestionan
con Alembic.

## Requisitos

- Python 3.12 o superior (ver `.python-version`).
- [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias.
- PostgreSQL 14 o superior (recomendado PostgreSQL 17).
- Git.

## Instalación

Desde la raíz del repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd Proyecto-IS1-2026
uv sync --frozen
```

`uv sync --frozen` instala las dependencias de `pyproject.toml` usando `uv.lock`,
incluido el grupo de desarrollo (`pytest`, `pytest-cov` y `ruff`).

### 1. Crear la base de datos

Conectar a PostgreSQL como superusuario y ejecutar:

```sql
CREATE ROLE is1_app LOGIN PASSWORD 'cambiarme';
CREATE DATABASE proyecto_is1_2026 OWNER is1_app;
CREATE DATABASE proyecto_is1_2026_test OWNER is1_app;
```

Ajustar los nombres y la contraseña según tu `.env`.

### 2. Configurar el entorno

Copiar el ejemplo y completar los valores:

```bash
cp .env.example .env
```

En Windows:

```powershell
copy .env.example .env
```

Como mínimo, definir `DB_PASSWORD` y `SECRET_KEY`. `python-dotenv` carga `.env`
automáticamente cuando la aplicación o Alembic importan `qanda.config`.

### 3. Aplicar las migraciones

```bash
uv run alembic upgrade head
```

Esto crea el esquema `is1`, las tablas y carga las categorías y etiquetas
iniciales. Ver la sección [Migraciones](#migraciones) para más comandos.

### 4. Ejecutar la aplicación

```bash
uv run flask --app qanda run --debug
```

Flask detecta automáticamente la fábrica `create_app()` en el paquete `qanda`.
Por defecto se usa `APP_ENV=development`.

## Variables de entorno

Las variables se leen desde el entorno o desde `.env`:

| Variable | Obligatoria | Valor por defecto | Uso |
| --- | :---: | --- | --- |
| `APP_ENV` | No | `development` | Selecciona la configuración: `development`, `testing` o `production`. |
| `SECRET_KEY` | En producción y desarrollo | — | Firma de sesiones de Flask. `TestingConfig` usa una clave fija. |
| `DB_USER` | No | `is1_app` | Usuario de PostgreSQL. |
| `DB_PASSWORD` | Según el servidor | — | Contraseña de PostgreSQL. |
| `DB_HOST` | No | `localhost` | Host de PostgreSQL. |
| `DB_PORT` | No | `5432` | Puerto de PostgreSQL. |
| `DB_NAME` | No | `proyecto_is1_2026` | Base de datos de desarrollo. |
| `DB_TEST_NAME` | No | `proyecto_is1_2026_test` | Base de datos de testing. |
| `DB_PROD_NAME` | En producción | — | Nombre de la base de producción. |
| `DB_PROD_USER` | En producción | — | Usuario de la base de producción. |
| `DB_PROD_PASSWORD` | En producción | — | Contraseña de la base de producción. |
| `TEST_DATABASE_URL` | Para las pruebas | — | URL de una base de mantenimiento con permiso `CREATEDB`; el fixture crea y elimina una base descartable. |
| `OPENAI_API_KEY` | Solo para `EstratOpenAI` | — | Credencial de OpenAI. |
| `GEMINI_API_KEY` | Solo para `EstratGemini` | — | Credencial de Google Gemini. |
| `OPENAI_MODEL` | No | `gpt-5.5` | Modelo usado por OpenAI. |
| `GEMINI_MODEL` | No | `gemini-3.8-flash` | Modelo usado por Gemini. |

Ejemplo de `TEST_DATABASE_URL`:

```bash
export TEST_DATABASE_URL="postgresql+psycopg://usuario:password@localhost:5432/postgres"
```

En Windows:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://usuario:password@localhost:5432/postgres"
```

Las pruebas no necesitan `.env` ni datos cargados: crean su propia base con el
esquema generado desde los modelos.

## Migraciones

Los comandos se ejecutan desde la raíz del proyecto y usan `alembic.ini`:

```bash
uv run alembic current
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic history
uv run alembic revision --autogenerate -m "descripcion"
```

`migrations/env.py` obtiene la URL de conexión desde `obtener_configuracion()`,
que lee `APP_ENV` y las variables `DB_*`. El valor `sqlalchemy.url` en
`alembic.ini` es solo un placeholder y no se usa directamente.

Las revisiones actuales son:

1. `d571f6d0f4cb`: crea el esquema `is1` y las tablas iniciales.
2. `57ab95d7f961`: inserta categorías y etiquetas iniciales de forma idempotente.

`baseDeDatos/schema.sql` contiene inserciones y consultas de verificación que
pueden aplicarse si se necesita repetir la carga:

```bash
psql -h localhost -U is1_app -d proyecto_is1_2026 -f baseDeDatos/schema.sql
```

No hace falta aplicarlo para ejecutar las pruebas.

## Pruebas y calidad

Las pruebas usan una base PostgreSQL descartable: crean una base nueva con un
nombre único, generan el esquema `is1` desde los modelos y la eliminan al
finalizar. No hace falta cargar datos de ejemplo ni configurar `.env`.

```bash
uv run pytest                          # con reporte de cobertura
uv run pytest --cov-report=html        # reporte HTML en htmlcov/
uv run ruff check .                    # lint sobre todo el proyecto
```

La cobertura se informa pero no hace fallar la suite: no hay `fail_under`
configurado.

GitHub Actions ejecuta automáticamente `pytest` y `ruff check .` en cada push y
pull request. El job de pruebas levanta un servicio PostgreSQL temporal y define
`TEST_DATABASE_URL` por medio de variables de entorno.

## Servicio de Respuestas Automáticas

La documentación de las estrategias de IA, sus variables de entorno y su uso se
encuentra en [`README_SRA.md`](README_SRA.md).
