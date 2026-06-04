"""Compatibilidad: reexporta el orquestador del asesor AWS."""

from backend.models import ContextoNegocio, EstimadoCostoAWS, PropuestaCompletaAWS
from backend.services.orchestrator import (
    AdvisorSession,
    ProcessResult,
    actualizar_contexto,
    crear_sesion,
    procesar_consulta,
    reiniciar_sesion,
)

# Alias para código existente
CalculatorSession = AdvisorSession


async def procesar_mensaje(sesion: AdvisorSession, texto: str) -> ProcessResult:
    """Procesa un mensaje (pipeline completo del asesor)."""
    return await procesar_consulta(sesion, texto)


__all__ = [
    'AdvisorSession',
    'CalculatorSession',
    'ContextoNegocio',
    'EstimadoCostoAWS',
    'ProcessResult',
    'PropuestaCompletaAWS',
    'actualizar_contexto',
    'crear_sesion',
    'procesar_consulta',
    'procesar_mensaje',
    'reiniciar_sesion',
]
