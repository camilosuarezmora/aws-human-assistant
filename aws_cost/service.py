"""Orquestación compartida entre CLI y GUI."""

from dataclasses import dataclass, field

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

from aws_cost.agent import crear_agente
from aws_cost.models import EstimadoCostoAWS
from aws_cost.prompt_validator import crear_validador, mensaje_advertencia, validar_prompt


@dataclass
class CalculatorSession:
    """Estado de una sesión de calculadora (agente + memoria)."""

    agent: Agent
    validador: Agent
    history: list[ModelMessage] = field(default_factory=list)


@dataclass
class ProcessResult:
    """Resultado de procesar un mensaje del usuario."""

    ok: bool
    estimacion: EstimadoCostoAWS | None = None
    advertencia: str | None = None
    error: str | None = None


def crear_sesion() -> CalculatorSession:
    """Crea agente, validador e historial vacío."""
    return CalculatorSession(
        agent=crear_agente(),
        validador=crear_validador(),
    )


async def procesar_mensaje(sesion: CalculatorSession, texto: str) -> ProcessResult:
    """
    Valida el prompt y, si es relevante, ejecuta el agente con tools.
    Actualiza el historial de la sesión solo en ejecuciones exitosas.
    """
    texto = texto.strip()
    if not texto:
        return ProcessResult(ok=False, advertencia='Escribe una pregunta sobre costos AWS.')

    try:
        validacion = await validar_prompt(
            sesion.validador,
            texto,
            es_seguimiento=bool(sesion.history),
        )
        if not validacion.es_relevante:
            return ProcessResult(ok=False, advertencia=mensaje_advertencia(validacion))

        resultado = await sesion.agent.run(texto, message_history=sesion.history)
        sesion.history += resultado.new_messages()
        return ProcessResult(ok=True, estimacion=resultado.output)

    except Exception as e:
        return ProcessResult(ok=False, error=str(e))


def reiniciar_sesion(sesion: CalculatorSession) -> None:
    """Borra el historial de conversación del agente."""
    sesion.history.clear()
