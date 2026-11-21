# Servicio de Respuestas Automáticas (SRA)

La implementación de Strategy se encuentra en `src/qanda/services/`.

## Clases

- `EstrategiaGeneracion`: interfaz abstracta común.
- `EstratOpenAI`: implementación con la API de OpenAI.
- `EstratGemini`: implementación con Google Gemini.
- `EstratModLocal`: placeholder; lanza `NotImplementedError` hasta que se elija un modelo local.
- `SRA`: contexto de Strategy; delega la generación en la estrategia seleccionada.

La clase persistente `qanda.models.AgenteIA` no se reemplaza. Es la entidad SQLAlchemy que representa al agente como `Autor` en la base de datos. `qanda.services.SRA` es el servicio que realiza la generación.

## Instalación

```bash
uv lock
```

`openai` y `google-genai` ya están declaradas en `pyproject.toml`; este comando regenera `uv.lock` para incorporar ambas dependencias.

## Variables de entorno

Configurar las claves fuera del código fuente:

```bash
export OPENAI_API_KEY="..."
export GEMINI_API_KEY="..."
```

Opcionalmente, se pueden seleccionar los modelos mediante:

```bash
export OPENAI_MODEL="gpt-5.5"
export GEMINI_MODEL="gemini-3.8-flash"
```

## Uso

```python
from qanda.models import Pregunta
from qanda.services import EstratOpenAI, SRA

pregunta = Pregunta(
    titulo="¿Qué es Python?",
    cuerpo="¿Cuáles son sus principales características?",
)

sra = SRA(EstratOpenAI())
texto_respuesta = sra.generar(pregunta)
```

Para cambiar de proveedor:

```python
from qanda.services import EstratGemini

sra.cambiar_estrategia(EstratGemini())
```

La generación devuelve texto. La creación y persistencia de una instancia `Respuesta` con un `AgenteIA` como autor debe realizarse desde el flujo de aplicación que invoque al SRA, porque el servicio no abre sesiones de base de datos ni guarda entidades.

## Pruebas

Se agregaron pruebas unitarias en `tests/test_sra.py`. Los clientes de los proveedores se pueden inyectar en los constructores para probar sin claves ni llamadas reales a las APIs.
