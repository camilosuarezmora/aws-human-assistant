# Calculadora de costos AWS con Pydantic AI

Aplicación que estima costos de infraestructura en **AWS** a partir de preguntas en lenguaje natural. Un agente de [Pydantic AI](https://ai.pydantic.dev/) interpreta la solicitud, invoca herramientas de precios y devuelve un desglose estructurado (`EstimadoCostoAWS`). Incluye interfaz de **línea de comandos** y **interfaz web** con Streamlit.

## Características

- Agente con **tool calling** para calcular costos por servicio AWS
- Salida tipada con **Pydantic** (ítems, totales mensual/anual, notas)
- **CLI** y **GUI** comparten la misma lógica de negocio (`aws_cost/service.py`)
- Validación de prompts para rechazar preguntas fuera de tema
- Historial de conversación dentro de cada sesión

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

## Stack tecnológico

| Tecnología | Uso |
|------------|-----|
| **Python 3.10+** | Lenguaje base |
| **Pydantic AI** (`pydantic-ai-slim[groq]`) | Agente, tools y proveedor LLM |
| **Groq** (`llama-3.3-70b-versatile`) | Modelo de lenguaje |
| **Pydantic** | Modelos y validación de salida |
| **Streamlit** | Interfaz gráfica |
| **python-dotenv** | Variables de entorno (`GROQ_API_KEY`) |

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

## Ejecución

### CLI interactiva

```bash
python main.py
```

Escribe preguntas sobre costos AWS. Para salir: `salir`, `exit`, `quit` o `q`.

**Ejemplos de preguntas:**

- ¿Cuánto cuestan 3 instancias t3.medium?
- Necesito 1 RDS db.t3.small con 100 GB de storage
- Calcula: 2× t3.micro, 50 GB S3, 1 RDS t3.small
- App con Lambda + API Gateway + DynamoDB

### Interfaz gráfica (Streamlit)

```bash
python main.py --gui
```

o directamente:

```bash
streamlit run gui.py
```

Se abrirá la calculadora en el navegador (por defecto en `http://localhost:8501`).

### Ejemplo mínimo (opcional)

[`hello_world.py`](hello_world.py) es un chat sencillo con Pydantic AI y Groq, **sin** herramientas ni lógica AWS. Sirve como punto de partida para probar el SDK:

```bash
python hello_world.py
```

## Estructura del proyecto

```
pydantic-ai/
├── main.py              # Entrada: CLI o --gui
├── gui.py               # Entrada Streamlit
├── hello_world.py       # Demo opcional de Pydantic AI
├── requirements.txt
├── .env.example
└── aws_cost/
    ├── agent.py         # Agente principal y system prompt
    ├── service.py       # Orquestación compartida CLI/GUI
    ├── cli.py           # Bucle interactivo de terminal
    ├── models.py        # EstimadoCostoAWS, CostoItem, etc.
    ├── tools.py         # Herramientas expuestas al agente
    ├── pricing.py       # Tablas de precios aproximados
    ├── prompt_validator.py
    ├── presentation.py  # Formato de salida en texto
    └── ui/              # Componentes Streamlit
```

## Flujo de la aplicación

```mermaid
flowchart LR
  user[Usuario] --> entry[main.py o gui.py]
  entry --> service[service.procesar_mensaje]
  service --> validator[Validador de prompt]
  validator -->|relevante| agent[Agente Pydantic AI]
  agent --> tools[Tools de pricing]
  tools --> output[EstimadoCostoAWS]
  output --> ui[CLI o Streamlit]
```

1. El usuario envía una pregunta en lenguaje natural.
2. Un validador comprueba que la pregunta sea sobre costos AWS.
3. El agente elige las herramientas adecuadas y calcula precios.
4. Se devuelve un `EstimadoCostoAWS` formateado en terminal o en la web.

## Limitaciones y avisos

- Los precios son **aproximados** y se basan en tablas estáticas en `aws_cost/pricing.py`.
- Por defecto se usa la región **us-east-1** (N. Virginia) salvo que indiques otra en la pregunta.
- **No** se incluyen impuestos, AWS Free Tier, Reserved Instances ni descuentos por volumen.
- Las estimaciones no sustituyen la [Calculadora de precios de AWS](https://calculator.aws/) ni facturación real.
- La aplicación requiere acceso a la **API de Groq**; sin `GROQ_API_KEY` válida no funcionará el agente.

## Referencias

- [Documentación de Pydantic AI](https://ai.pydantic.dev/)
- [Groq Console](https://console.groq.com/)
- [AWS Pricing](https://aws.amazon.com/pricing/)

## Licencia

Este repositorio no incluye un archivo de licencia explícito. Consulta al autor antes de reutilizar el código en otros proyectos.
