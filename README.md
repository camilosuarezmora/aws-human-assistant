# Asesor AWS con Pydantic AI

Aplicación que ayuda a personas **sin conocimientos técnicos** a traducir problemas de negocio en soluciones **AWS** con costes estimados y una hoja de ruta de implementación. Usa [Pydantic AI](https://ai.pydantic.dev/) con un pipeline multi-agente (validación → arquitectura → costos → hoja de ruta). Incluye **formulario inicial** + **chat** en Streamlit y **CLI**.

## Características

- **Intake híbrido:** formulario de negocio + chat para afinar
- **Pipeline multi-agente:** arquitecto, calculador con tools, generador de hoja de ruta (IAM/VPC)
- **Tool calling** para ~18 servicios AWS (EC2, RDS, Lambda, ALB, CloudFront, Fargate, etc.)
- Salida tipada: `PropuestaCompletaAWS` (arquitectura, `EstimadoCostoAWS`, `HojaRutaAWS`)
- Comparación con **presupuesto** del intake y rediseño automático si se excede
- Exportación de propuesta en **Markdown**
- **CLI** y **GUI** comparten `backend/services/orchestrator.py`
- Precios EC2/RDS vía AWS Price List API (opcional); resto con tablas de referencia

### Servicios AWS soportados

| Herramienta | Servicio |
|-------------|----------|
| `costo_ec2` | EC2 |
| `costo_rds` | RDS |
| `costo_elasticache` | ElastiCache (Redis/Memcached) |
| `costo_s3` | S3 |
| `costo_transferencia_datos` | Transferencia de datos saliente |
| `costo_lambda` | Lambda |
| `costo_api_gateway` | API Gateway |
| `costo_dynamodb` | DynamoDB |
| `costo_sns` | SNS |
| `costo_sqs` | SQS |
| `costo_alb` | Application Load Balancer |
| `costo_cloudfront` | CloudFront |
| `costo_route53` | Route 53 |
| `costo_fargate` | Fargate |
| `costo_ecs` | ECS |
| `costo_cognito` | Cognito |
| `costo_cloudwatch` | CloudWatch Logs |
| `costo_nat_gateway` | NAT Gateway |

## Stack tecnológico

| Tecnología | Uso |
|------------|-----|
| **Python 3.10+** | Lenguaje base |
| **Pydantic AI** (`pydantic-ai-slim[groq]`) | Agente, tools y proveedor LLM |
| **Groq** (`llama-3.3-70b-versatile`) | Modelo de lenguaje |
| **Pydantic** | Modelos y validación de salida |
| **Streamlit** | Interfaz gráfica |
| **python-dotenv** | Variables de entorno (`GROQ_API_KEY`, credenciales AWS) |
| **boto3** | AWS Price List API (EC2 y RDS con caché) |

## Arquitectura

El código se organiza en dos capas con dependencia unidireccional:

```mermaid
flowchart TB
  subgraph root [Raíz del proyecto]
    main[main.py]
    gui[gui.py]
    hello[hello_world.py]
  end

  subgraph frontend_layer [frontend — presentación]
    fcli[cli/app.py]
    fst[streamlit/app.py]
    fcomp[streamlit/components.py]
    ffmt[formatters.py]
  end

  subgraph backend_layer [backend — dominio]
    svc[services/calculator.py]
    agt_calc[agents/calculator.py]
    agt_val[agents/validator.py]
    agt_base[agents/base.py]
    tools[tools.py]
    pricing[pricing.py]
    models[models.py]
    config[config.py]
  end

  subgraph external [Externos]
    groq[Groq API]
  end

  main --> fcli
  main --> gui
  gui --> fst
  fcli --> svc
  fcli --> ffmt
  fst --> svc
  fst --> ffmt
  fcomp --> ffmt
  fcomp --> svc
  svc --> agt_val
  svc --> agt_calc
  agt_calc --> tools
  agt_calc --> agt_base
  agt_val --> agt_base
  tools --> pricing
  tools --> models
  agt_calc --> models
  agt_val --> models
  agt_base --> config
  agt_calc --> groq
  agt_val --> groq
```

| Regla | Descripción |
|-------|-------------|
| **Frontend → Backend** | `frontend/` solo importa desde `backend/`. Nunca al revés. |
| **Sin UI en backend** | `backend/` no importa Streamlit ni código de terminal. |
| **Punto único de orquestación** | Toda petición del usuario pasa por `procesar_mensaje()` en `backend/services/calculator.py`. |
| **Precios** | EC2/RDS: `pricing_resolver.py` (API + caché + fallback a `pricing.py`); otros servicios: solo `pricing.py`. |

## Mapa del código

Árbol completo con el rol de cada archivo. Úsalo como índice para navegar el repositorio.

```
pydantic-ai/
│
├── main.py                      # Dispatcher: carga .env, CLI o lanza Streamlit (--gui)
├── gui.py                       # Entrada mínima Streamlit (env + run_app)
├── hello_world.py               # Demo aislada del SDK (no usa backend/frontend)
├── requirements.txt             # Dependencias Python
├── .env.example                 # Plantilla GROQ_API_KEY
│
├── backend/                     # CAPA DE DOMINIO
│   ├── __init__.py              # API pública: crear_sesion, procesar_mensaje, modelos…
│   ├── config.py                # PROJECT_ROOT, GROQ_MODEL_NAME, load_environment()
│   ├── models.py                # CostoItem, EstimadoCostoAWS, ValidacionPrompt
│   ├── pricing.py               # Diccionarios estáticos y fallback USD
│   ├── aws_pricing_client.py    # Cliente boto3 GetProducts (EC2/RDS)
│   ├── pricing_cache.py         # Caché en memoria con TTL
│   ├── pricing_resolver.py      # API + caché + fallback para tools EC2/RDS
│   ├── tools.py                 # Funciones @tool para el agente + ALL_TOOLS
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # crear_modelo_groq() — factory compartida
│   │   ├── calculator.py        # Agente principal + SYSTEM_PROMPT + crear_agente()
│   │   └── validator.py         # Agente clasificador + validar_prompt()
│   │
│   └── services/
│       ├── __init__.py
│       └── calculator.py        # CalculatorSession, ProcessResult, procesar_mensaje()
│
└── frontend/                    # CAPA DE PRESENTACIÓN
    ├── __init__.py
    ├── formatters.py            # Texto plano y filas para tablas Streamlit
    │
    ├── cli/
    │   ├── __init__.py          # exporta run
    │   └── app.py               # Bucle input/print de terminal
    │
    └── streamlit/
        ├── __init__.py          # exporta run_app
        ├── app.py               # Página principal, chat_input, session_state
        └── components.py        # Sidebar, historial, métricas y dataframe
```

### Puntos de entrada

| Archivo | Comando | Qué hace |
|---------|---------|----------|
| [`main.py`](main.py) | `python main.py` | Ejecuta la CLI (`frontend.cli.app.run`) |
| [`main.py`](main.py) | `python main.py --gui` | Lanza Streamlit sobre [`gui.py`](gui.py) |
| [`gui.py`](gui.py) | `streamlit run gui.py` | Carga entorno y llama `frontend.streamlit.app.run_app` |
| [`hello_world.py`](hello_world.py) | `python hello_world.py` | Chat de prueba sin calculadora AWS |

---

## Especificación por carpeta

### Raíz (`/`)

| Archivo | Responsabilidad | Dependencias clave |
|---------|-----------------|-------------------|
| `main.py` | Argumentos CLI/GUI; carga `.env` al importar | `backend.config`, `frontend.cli` |
| `gui.py` | Wrapper de una línea para Streamlit | `backend.config`, `frontend.streamlit.app` |
| `hello_world.py` | Ejemplo independiente de Pydantic AI + Groq | Solo `pydantic_ai`, `dotenv` |
| `.env.example` | `GROQ_API_KEY` y credenciales AWS opcionales para precios en vivo | — |
| `pytest.ini` | Configuración de tests (`tests/`) | — |

---

### `backend/` — Lógica de negocio

Paquete sin dependencias de UI. Contiene modelos, precios, agentes LLM y la orquestación de sesiones.

#### `backend/config.py`

| Elemento | Descripción |
|----------|-------------|
| `PROJECT_ROOT` | Ruta a la raíz del repo (para localizar `.env`) |
| `GROQ_MODEL_NAME` | Modelo por defecto: `llama-3.3-70b-versatile` |
| `DEFAULT_REGION` | Región AWS por defecto: `us-east-1` |
| `load_environment()` | Carga `PROJECT_ROOT/.env` con `python-dotenv` |
| `pricing_api_region()` | Endpoint del cliente pricing (`PRICING_API_REGION`, default `us-east-1`) |
| `pricing_cache_ttl_seconds()` | TTL de caché (`PRICING_CACHE_TTL_SECONDS`, default 86400) |
| `aws_pricing_enabled()` | Activa/desactiva API (`AWS_PRICING_ENABLED`, default true) |

#### `backend/models.py`

| Modelo | Campos relevantes | Uso |
|--------|-------------------|-----|
| `CostoItem` | servicio, descripción, cantidad, costos | Un recurso AWS en el desglose |
| `EstimadoCostoAWS` | items, total_mensual, total_anual, region, notas | Salida estructurada del agente principal |
| `ValidacionPrompt` | es_relevante, categoria, mensaje | Salida del agente validador |

Categorías del validador: `aws_costos`, `off_topic`, `ambiguo`.

#### `backend/pricing.py`

Tablas y constantes en USD (referencia aproximada, región us-east-1):

- `PRECIOS_EC2_US_EAST_1`, `PRECIOS_RDS_US_EAST_1`, `PRECIOS_ELASTICACHE`
- Constantes unitarias: S3, transferencia, Lambda, API Gateway, DynamoDB, SNS, SQS, storage RDS

Datos estáticos editables y **fallback** cuando la API no está disponible o falla.

#### `backend/aws_pricing_client.py`, `pricing_cache.py`, `pricing_resolver.py`

- **Cliente**: `get_products` / `precio_on_demand_hora` con filtros EC2 (Linux On-Demand) y RDS (MySQL Single-AZ por defecto).
- **Caché**: clave por servicio, región e instancia; TTL configurable (24 h por defecto).
- **Resolver**: `precio_ec2_mensual`, `precio_rds_mensual` (730 h/mes); sin credenciales o con `AWS_PRICING_ENABLED=false` usa solo `pricing.py`.

IAM mínimo recomendado: `pricing:GetProducts`, `pricing:DescribeServices`, `pricing:GetAttributeValues`.

#### `backend/tools.py`

Funciones registradas como tools del agente:

- **EC2/RDS**: precios vía `pricing_resolver` (API + caché + fallback).
- **Resto**: lectura directa de `pricing.py`.
- Devuelven un `CostoItem`.

Lista exportada: `ALL_TOOLS` (9 herramientas, ver tabla de servicios arriba).

#### `backend/agents/`

| Archivo | Rol |
|---------|-----|
| `base.py` | `crear_modelo_groq()` — evita duplicar configuración del modelo |
| `calculator.py` | Agente con `ALL_TOOLS`, `SYSTEM_PROMPT` y `output_type=EstimadoCostoAWS` |
| `validator.py` | Agente sin tools; clasifica prompts; `validar_prompt()`, `mensaje_advertencia()` |

#### `backend/services/calculator.py`

**Núcleo de la aplicación.** API que consumen CLI y Streamlit:

| Símbolo | Tipo | Descripción |
|---------|------|-------------|
| `CalculatorSession` | dataclass | Agente + validador + `history` (mensajes Pydantic AI) |
| `ProcessResult` | dataclass | `ok`, `estimacion`, `advertencia`, `error` |
| `crear_sesion()` | función | Instancia agentes e historial vacío |
| `procesar_mensaje(sesion, texto)` | async | Valida → ejecuta agente → actualiza historial |
| `reiniciar_sesion(sesion)` | función | Limpia `history` (botón “Nueva conversación” en GUI) |

Flujo interno de `procesar_mensaje`:

1. Texto vacío → advertencia
2. `validar_prompt()` → si no es relevante → advertencia con mensaje del validador
3. `agent.run()` con tools → `EstimadoCostoAWS`
4. Excepciones → `ProcessResult.error`

#### `backend/__init__.py`

Reexporta la API pública para uso programático:

```python
from backend import crear_sesion, procesar_mensaje, EstimadoCostoAWS, load_environment
```

---

### `frontend/` — Presentación

Solo formatea y muestra resultados; no define precios ni agentes.

#### `frontend/formatters.py`

| Función | Salida | Consumidor |
|---------|--------|------------|
| `formatear_estimacion_texto()` | Tabla ASCII + totales + notas | CLI, historial de chat Streamlit |
| `estimacion_a_filas()` | `list[dict]` para `st.dataframe` | `streamlit/components.py` |

#### `frontend/cli/`

| Archivo | Contenido |
|---------|-----------|
| `app.py` | Banner, bucle `input()`, llama `procesar_mensaje`, imprime con `formatear_estimacion_texto` |
| `__init__.py` | Exporta `run` (función async del bucle) |

Comandos de salida: `salir`, `exit`, `quit`, `q`.

#### `frontend/streamlit/`

| Archivo | Contenido |
|---------|-----------|
| `app.py` | `run_app()`: page config, `session_state` (`ui_messages`, `calculator_session`), `chat_input`, `asyncio.run` por mensaje |
| `components.py` | `render_sidebar()`, `render_estimacion()`, `render_chat_history()` |

Estado en Streamlit:

- `calculator_session` → `CalculatorSession` del backend
- `ui_messages` → lista de mensajes UI (rol, contenido, estimación opcional)

---

## Flujo de una petición (secuencia)

```mermaid
sequenceDiagram
  participant U as Usuario
  participant F as frontend
  participant S as services.calculator
  participant V as agents.validator
  participant A as agents.calculator
  participant T as backend.tools

  U->>F: Pregunta en lenguaje natural
  F->>S: procesar_mensaje(sesion, texto)
  S->>V: validar_prompt()
  alt No relevante
    V-->>S: ValidacionPrompt
    S-->>F: ProcessResult.advertencia
    F-->>U: Mensaje de aviso
  else Relevante
    S->>A: agent.run(texto, history)
    A->>T: tool calls (costo_ec2, costo_s3, ...)
    T-->>A: CostoItem
    A-->>S: EstimadoCostoAWS
    S-->>F: ProcessResult.estimacion
    F->>F: formatters
    F-->>U: Tabla / texto formateado
  end
```

## Requisitos previos

- Python 3.10 o superior
- Cuenta en [Groq](https://console.groq.com/) con API key
- Conexión a internet (llamadas a la API de Groq)

Se recomienda usar un entorno virtual (`.venv`).

## Instalación

```bash
git clone https://github.com/camilosuarezmora/pydantic-ai.git
cd pydantic-ai
python -m venv .venv
```

Activar el entorno virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

Instalar dependencias y configurar la API key:

```bash
pip install -r requirements.txt

# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Edita `.env` y define tu clave:

```env
GROQ_API_KEY=tu_clave_aqui
```

Los archivos `.env` y `.venv/` están en `.gitignore` y no deben subirse al repositorio.

> Ejecuta siempre los comandos desde la **raíz del proyecto** para que Python resuelva los paquetes `backend` y `frontend`.

## Ejecución

### CLI interactiva

```bash
python main.py
```

**Ejemplos de preguntas:**

- ¿Cuánto cuestan 3 instancias t3.medium?
- Necesito 1 RDS db.t3.small con 100 GB de storage
- Calcula: 2× t3.micro, 50 GB S3, 1 RDS t3.small
- App con Lambda + API Gateway + DynamoDB

### Interfaz gráfica (Streamlit)

```bash
python main.py --gui
# o
streamlit run gui.py
```

Se abrirá la calculadora en el navegador (por defecto en `http://localhost:8501`).

### Ejemplo mínimo (opcional)

[`hello_world.py`](hello_world.py) es un chat sencillo con Pydantic AI y Groq, **sin** herramientas ni lógica AWS:

```bash
python hello_world.py
```

## Dónde empezar a leer el código

| Si quieres… | Empieza por… |
|-------------|--------------|
| Entender el flujo completo | [`backend/services/calculator.py`](backend/services/calculator.py) |
| Ver cómo se calcula un precio EC2/RDS | [`backend/tools.py`](backend/tools.py) → [`backend/pricing_resolver.py`](backend/pricing_resolver.py) |
| Precios estáticos / fallback | [`backend/pricing.py`](backend/pricing.py) |
| Cambiar el comportamiento del LLM | [`backend/agents/calculator.py`](backend/agents/calculator.py) |
| Ajustar qué preguntas se aceptan | [`backend/agents/validator.py`](backend/agents/validator.py) |
| Modificar la terminal | [`frontend/cli/app.py`](frontend/cli/app.py) |
| Modificar la web | [`frontend/streamlit/app.py`](frontend/streamlit/app.py) |
| Cambiar cómo se muestran los totales | [`frontend/formatters.py`](frontend/formatters.py) |
| Añadir una nueva UI (p. ej. FastAPI) | Crea módulo en `frontend/` que llame solo a `procesar_mensaje` |

## Precios en vivo (EC2 y RDS)

1. Copia variables de [`.env.example`](.env.example) y configura `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (o perfil `~/.aws/credentials`).
2. Con credenciales válidas, `costo_ec2` y `costo_rds` consultan la [AWS Price List Query API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html); los resultados se cachean en memoria.
3. Sin credenciales o si la API falla, se usan las tablas de [`backend/pricing.py`](backend/pricing.py) sin interrumpir la app.

```bash
pip install -r requirements.txt
pytest -m "not integration"
# Con AWS configurado:
pytest -m integration
```

## Limitaciones y avisos

- **EC2/RDS** pueden usar precios API; el resto de servicios siguen en tablas estáticas (`pricing.py`).
- El fallback estático solo cataloga **us-east-1**; otras regiones en fallback usan esos valores como aproximación.
- RDS vía API asume **MySQL Single-AZ** On-Demand salvo ampliación futura de parámetros.
- Conversión mensual: precio hora × **730** (convención tipo AWS Calculator).
- **No** se incluyen impuestos, AWS Free Tier, Reserved Instances ni descuentos por volumen.
- Las estimaciones no sustituyen la [Calculadora de precios de AWS](https://calculator.aws/) ni facturación real.
- La aplicación requiere **Groq** (`GROQ_API_KEY`); AWS es opcional solo para precios EC2/RDS.

## Referencias

- [Documentación de Pydantic AI](https://ai.pydantic.dev/)
- [Groq Console](https://console.groq.com/)
- [AWS Pricing](https://aws.amazon.com/pricing/)

## Licencia

Este repositorio no incluye un archivo de licencia explícito. Consulta al autor antes de reutilizar el código en otros proyectos.
