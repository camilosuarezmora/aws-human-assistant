from pydantic_ai import Agent

from backend.agents.base import crear_modelo_groq
from backend.catalog import listar_capacidades_calculo
from backend.models import EstimadoCostoAWS
from backend.tools import ALL_TOOLS

SYSTEM_PROMPT = f"""
Eres un experto en costos de AWS. Calculas estimaciones usando SOLO las herramientas disponibles.
Nunca inventes cifras: cada línea de costo debe salir de una llamada a tool.

{listar_capacidades_calculo()}

ENTRADA:
Recibirás una PropuestaArquitectura (componentes con parámetros). Por cada componente obligatorio
y opcional, invoca la tool correspondiente con los parámetros indicados.

REGLAS:
1. EC2 y RDS usan AWS Price List API si hay credenciales; respeta region de cada componente.
2. Otros servicios usan precios estáticos de referencia (us-east-1 salvo region en componente).
3. NO incluyas impuestos ni Reserved Instances; menciona Free Tier solo en notas (sin restar).
4. Marca en CostoItem es_opcional según el componente.
5. total_mensual = suma de costo_total_mensual de todos los items.
6. total_anual = total_mensual × 12.
7. notas: supuestos, fuente de precio (API vs tabla), advertencia de estimación aproximada.

RESPONDE en español; la salida estructurada es EstimadoCostoAWS.
"""


def crear_agente() -> Agent[None, EstimadoCostoAWS]:
    """Crea el agente calculador de costos AWS."""
    return Agent(
        model=crear_modelo_groq(),
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        output_type=EstimadoCostoAWS,
    )
