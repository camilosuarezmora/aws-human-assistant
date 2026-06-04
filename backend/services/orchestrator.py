"""Pipeline multi-agente: validación → arquitectura → costos → hoja de ruta."""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

from backend.agents.architect import crear_arquitecto
from backend.agents.calculator import crear_agente
from backend.agents.roadmap import crear_roadmap
from backend.agents.validator import crear_validador, mensaje_advertencia, validar_prompt
from backend.models import (
    ContextoNegocio,
    EstimadoCostoAWS,
    PropuestaArquitectura,
    PropuestaCompletaAWS,
)


@dataclass
class AdvisorSession:
    """Estado de sesión del asesor AWS."""

    arquitecto: Agent
    calculador: Agent
    roadmap_agent: Agent
    validador: Agent
    contexto_negocio: ContextoNegocio | None = None
    history: list[ModelMessage] = field(default_factory=list)
    ultima_propuesta: PropuestaCompletaAWS | None = None


@dataclass
class ProcessResult:
    """Resultado de procesar un mensaje."""

    ok: bool
    propuesta: PropuestaCompletaAWS | None = None
    estimacion: EstimadoCostoAWS | None = None
    advertencia: str | None = None
    error: str | None = None
    fase: str | None = None


def crear_sesion(contexto: ContextoNegocio | None = None) -> AdvisorSession:
    """Crea agentes e historial vacío."""
    return AdvisorSession(
        arquitecto=crear_arquitecto(),
        calculador=crear_agente(),
        roadmap_agent=crear_roadmap(),
        validador=crear_validador(),
        contexto_negocio=contexto,
    )


def _prompt_con_contexto(contexto: ContextoNegocio | None, texto: str) -> str:
    partes = [texto.strip()]
    if contexto is not None:
        partes.insert(
            0,
            '--- Contexto del formulario inicial ---\n'
            + contexto.model_dump_json(indent=2, exclude_none=True),
        )
    return '\n\n'.join(partes)


def _serializar_arquitectura(propuesta: PropuestaArquitectura) -> str:
    return propuesta.model_dump_json(indent=2)


def _evaluar_presupuesto(
    total_mensual: float,
    contexto: ContextoNegocio | None,
) -> bool | None:
    if contexto is None or contexto.presupuesto_mensual_usd is None:
        return None
    return total_mensual <= contexto.presupuesto_mensual_usd


async def _optimizar_si_excede(
    sesion: AdvisorSession,
    arquitectura: PropuestaArquitectura,
    estimacion: EstimadoCostoAWS,
    contexto: ContextoNegocio | None,
) -> tuple[PropuestaArquitectura, EstimadoCostoAWS, list[str]]:
    """Segundo pase del arquitecto si se supera el presupuesto."""
    if contexto is None or contexto.presupuesto_mensual_usd is None:
        return arquitectura, estimacion, []
    if estimacion.total_mensual <= contexto.presupuesto_mensual_usd:
        return arquitectura, estimacion, []

    prompt_opt = (
        f'El coste mensual estimado (${estimacion.total_mensual:.2f}) supera el presupuesto '
        f'objetivo (${contexto.presupuesto_mensual_usd:.2f}). '
        'Rediseña la arquitectura eliminando componentes opcionales y reduciendo tamaños. '
        'Mantén la solución viable.\n\n'
        f'Arquitectura actual:\n{_serializar_arquitectura(arquitectura)}'
    )
    res_arch = await sesion.arquitecto.run(prompt_opt)
    nueva_arch = res_arch.output
    res_calc = await sesion.calculador.run(
        'Calcula costos para esta arquitectura optimizada:\n'
        + _serializar_arquitectura(nueva_arch),
    )
    nueva_est = res_calc.output
    tips = [
        'Se aplicó un rediseño automático para acercarse a tu presupuesto.',
        'Revisa componentes marcados como opcionales en la tabla de costes.',
    ]
    return nueva_arch, nueva_est, tips


async def procesar_consulta(
    sesion: AdvisorSession,
    texto: str,
    *,
    solo_costos: bool = False,
) -> ProcessResult:
    """
    Ejecuta el pipeline completo o solo recálculo de costos (mensajes aws_costos legacy).
    """
    texto = texto.strip()
    if not texto:
        return ProcessResult(ok=False, advertencia='Escribe tu pregunta o describe tu negocio.')

    try:
        validacion = await validar_prompt(
            sesion.validador,
            _prompt_con_contexto(sesion.contexto_negocio, texto),
            es_seguimiento=bool(sesion.history),
        )
        if not validacion.es_relevante:
            return ProcessResult(ok=False, advertencia=mensaje_advertencia(validacion))

        prompt_usuario = _prompt_con_contexto(sesion.contexto_negocio, texto)

        if solo_costos or validacion.categoria == 'aws_costos':
            resultado = await sesion.calculador.run(
                prompt_usuario,
                message_history=sesion.history,
            )
            sesion.history += resultado.new_messages()
            est = resultado.output
            if sesion.ultima_propuesta:
                sesion.ultima_propuesta.estimacion = est
                sesion.ultima_propuesta.cumple_presupuesto = _evaluar_presupuesto(
                    est.total_mensual,
                    sesion.contexto_negocio,
                )
                return ProcessResult(
                    ok=True,
                    propuesta=sesion.ultima_propuesta,
                    estimacion=est,
                    fase='costes',
                )
            return ProcessResult(ok=True, estimacion=est, fase='costes')

        res_arch = await sesion.arquitecto.run(prompt_usuario)
        arquitectura = res_arch.output

        res_calc = await sesion.calculador.run(
            'Calcula costos invocando tools para cada componente:\n'
            + _serializar_arquitectura(arquitectura),
        )
        estimacion = res_calc.output

        opciones_reduccion: list[str] = []
        arquitectura, estimacion, tips = await _optimizar_si_excede(
            sesion,
            arquitectura,
            estimacion,
            sesion.contexto_negocio,
        )
        opciones_reduccion.extend(tips)

        res_road = await sesion.roadmap_agent.run(
            'Genera la hoja de ruta para esta propuesta:\n\n'
            f'Arquitectura:\n{_serializar_arquitectura(arquitectura)}\n\n'
            f'Estimación:\n{estimacion.model_dump_json(indent=2)}',
        )
        hoja_ruta = res_road.output

        cumple = _evaluar_presupuesto(estimacion.total_mensual, sesion.contexto_negocio)
        if cumple is False and not opciones_reduccion:
            opciones_reduccion.append(
                f'El total mensual (${estimacion.total_mensual:.2f}) supera tu presupuesto '
                f'(${sesion.contexto_negocio.presupuesto_mensual_usd:.2f}). '
                'Puedes pedir en el chat que reduzcamos costes.'
            )

        propuesta = PropuestaCompletaAWS(
            arquitectura=arquitectura,
            estimacion=estimacion,
            hoja_ruta=hoja_ruta,
            cumple_presupuesto=cumple,
            opciones_reduccion_coste=opciones_reduccion,
        )
        sesion.ultima_propuesta = propuesta
        sesion.history += res_calc.new_messages()

        return ProcessResult(
            ok=True,
            propuesta=propuesta,
            estimacion=estimacion,
            fase='completo',
        )

    except Exception as e:
        return ProcessResult(ok=False, error=str(e))


def reiniciar_sesion(sesion: AdvisorSession) -> None:
    """Borra historial y última propuesta."""
    sesion.history.clear()
    sesion.ultima_propuesta = None


def actualizar_contexto(sesion: AdvisorSession, contexto: ContextoNegocio) -> None:
    """Actualiza el contexto de negocio del intake."""
    sesion.contexto_negocio = contexto
