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
1. Todos los precios provienen exclusivamente de la AWS Price List API vía tools; nunca inventes cifras.
2. Si una tool falla por precio no disponible, indícalo en notas y no sustituyas valores manualmente.
3. Respeta la region de cada componente al invocar las tools.
4. NO incluyas impuestos ni Reserved Instances; menciona Free Tier solo en notas (sin restar).
5. Marca en CostoItem es_opcional según el componente.
6. total_mensual = suma de costo_total_mensual de todos los items.
7. total_anual = total_mensual × 12.
8. notas: supuestos, fuente AWS Price List API, advertencia de estimación aproximada.

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
