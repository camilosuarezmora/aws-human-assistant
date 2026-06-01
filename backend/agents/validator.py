"""Clasificación de prompts antes de invocar el agente con tools."""

from pydantic_ai import Agent

from backend.agents.base import crear_modelo_groq
from backend.models import ValidacionPrompt

VALIDATOR_INSTRUCTIONS = """
Clasifica si el mensaje del usuario pertenece a esta aplicación: una calculadora de
COSTOS de infraestructura en AWS (EC2, RDS, S3, Lambda, API Gateway, DynamoDB,
ElastiCache, SNS, SQS, transferencia de datos, presupuestos mensuales/anuales).

RELEVANTE (es_relevante=true, categoria=aws_costos):
- Pide precios, estimaciones, presupuesto o comparación de costos en AWS.
- Describe recursos AWS concretos o arquitecturas a valorar.
- Seguimientos cortos en una conversación de costos ("añade 50GB S3", "y un RDS más",
  "duplica las instancias", "¿cuánto sería en total?").

NO RELEVANTE (es_relevante=false, categoria=off_topic):
- Temas sin relación con costos AWS: chistes, historia, deportes, programación general,
  otras nubes sin pedir costos, saludos sin intención de calcular nada.
- Preguntas sobre cómo usar AWS sin pedir dinero/costos.

AMBIGUO (es_relevante=false, categoria=ambiguo):
- No queda claro qué servicios AWS ni qué quiere estimar; pide aclaración en mensaje.

En mensaje, escribe en español una frase clara para el usuario cuando no sea relevante.
Si es relevante, mensaje puede ser una cadena vacía.
"""

MENSAJE_OFF_TOPIC = (
    'Esta herramienta solo estima costos de infraestructura AWS '
    '(EC2, RDS, S3, Lambda, API Gateway, DynamoDB, etc.).'
)


def crear_validador() -> Agent[None, ValidacionPrompt]:
    """Agente clasificador sin tools."""
    return Agent(
        model=crear_modelo_groq(),
        instructions=VALIDATOR_INSTRUCTIONS,
        output_type=ValidacionPrompt,
    )


async def validar_prompt(
    validador: Agent[None, ValidacionPrompt],
    texto: str,
    *,
    es_seguimiento: bool = False,
) -> ValidacionPrompt:
    """Clasifica el prompt del usuario antes de ejecutar tools de costos."""
    contexto = ''
    if es_seguimiento:
        contexto = (
            'Contexto: seguimiento en una conversación activa de costos AWS. '
            'Sé permisivo con mensajes cortos que amplían o ajustan la estimación anterior.\n\n'
        )
    resultado = await validador.run(contexto + texto)
    return resultado.output


def mensaje_advertencia(validacion: ValidacionPrompt) -> str:
    """Texto a mostrar cuando el prompt no debe activar el agente principal."""
    if validacion.mensaje.strip():
        return validacion.mensaje.strip()
    if validacion.categoria == 'ambiguo':
        return (
            'No quedó claro qué recursos AWS quieres estimar. '
            'Indica servicios y cantidades, por ejemplo: "2 instancias t3.medium y 100GB S3".'
        )
    return MENSAJE_OFF_TOPIC
