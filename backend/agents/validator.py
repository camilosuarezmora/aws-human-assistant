"""Clasificación de prompts antes de invocar el pipeline de asesoría."""

from pydantic_ai import Agent

from backend.agents.base import crear_modelo_groq
from backend.models import ValidacionPrompt

VALIDATOR_INSTRUCTIONS = """
Clasifica si el mensaje del usuario pertenece a esta aplicación: un ASESOR AWS que ayuda a
personas sin conocimientos técnicos a traducir problemas de negocio en soluciones en la nube
con estimación de costos (EC2, RDS, S3, Lambda, contenedores, CDN, bases de datos, etc.).

RELEVANTE (es_relevante=true):
- categoria=problema_negocio: describe un negocio, app, tienda, startup, necesidad sin jerga AWS.
- categoria=refinamiento: seguimiento en conversación activa ("añade base de datos", "menos presupuesto",
  "quita el CDN", "¿cuánto sería en total?", aclaraciones sobre usuarios o tráfico).
- categoria=aws_costos: pide precios o describe infraestructura AWS concreta a valorar.

NO RELEVANTE (es_relevante=false, categoria=off_topic):
- Chistes, deportes, programación general sin relación con AWS o su negocio en la nube.
- Otras nubes sin pedir solución/costos AWS.

AMBIGUO (es_relevante=false, categoria=ambiguo):
- No se entiende qué negocio o necesidad tiene; pide aclaración en lenguaje LLANO
  (ej. "¿Cuántas personas usarán tu aplicación al mismo tiempo?" — NO pidas tipos de instancia).

En mensaje, escribe en español una frase clara para el usuario cuando no sea relevante.
Si es relevante, mensaje puede ser cadena vacía.
"""

MENSAJE_OFF_TOPIC = (
    'Esta herramienta ayuda a diseñar soluciones en AWS y estimar sus costos. '
    'Cuéntanos qué negocio o aplicación quieres lanzar o mejorar.'
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
    """Clasifica el prompt del usuario antes del pipeline."""
    contexto = ''
    if es_seguimiento:
        contexto = (
            'Contexto: seguimiento en una conversación activa del asesor AWS. '
            'Sé permisivo con mensajes cortos que refinan la propuesta o los costes.\n\n'
        )
    resultado = await validador.run(contexto + texto)
    return resultado.output


def mensaje_advertencia(validacion: ValidacionPrompt) -> str:
    """Texto a mostrar cuando el prompt no debe activar el pipeline."""
    if validacion.mensaje.strip():
        return validacion.mensaje.strip()
    if validacion.categoria == 'ambiguo':
        return (
            'Necesito entender mejor tu situación. '
            '¿Qué tipo de negocio o aplicación es y cuántas personas la usarían aproximadamente?'
        )
    return MENSAJE_OFF_TOPIC
