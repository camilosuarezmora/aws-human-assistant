"""Tests del orquestador con agentes mockeados."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.models import (
    ComponenteAWS,
    ContextoNegocio,
    EstimadoCostoAWS,
    FaseHojaRuta,
    HojaRutaAWS,
    PropuestaArquitectura,
    PropuestaCompletaAWS,
    ValidacionPrompt,
)
from backend.services.orchestrator import (
    AdvisorSession,
    _evaluar_presupuesto,
    procesar_consulta,
)


def _sesion_mock(contexto: ContextoNegocio | None = None) -> AdvisorSession:
    """Sesión sin instanciar modelos Groq (tests sin API key)."""
    return AdvisorSession(
        arquitecto=MagicMock(),
        calculador=MagicMock(),
        roadmap_agent=MagicMock(),
        validador=MagicMock(),
        contexto_negocio=contexto,
    )


def _run_output(value):
    mock = MagicMock()
    mock.output = value
    mock.new_messages = MagicMock(return_value=[])
    return mock


@pytest.fixture
def contexto_con_presupuesto() -> ContextoNegocio:
    return ContextoNegocio(
        tipo_negocio='SaaS',
        problema='App de gestión',
        presupuesto_mensual_usd=100.0,
    )


def test_evaluar_presupuesto(contexto_con_presupuesto: ContextoNegocio):
    assert _evaluar_presupuesto(80.0, contexto_con_presupuesto) is True
    assert _evaluar_presupuesto(150.0, contexto_con_presupuesto) is False
    assert _evaluar_presupuesto(50.0, None) is None


def test_procesar_consulta_pipeline_mockeado(contexto_con_presupuesto: ContextoNegocio):
    sesion = _sesion_mock(contexto_con_presupuesto)

    arquitectura = PropuestaArquitectura(
        resumen_ejecutivo='Resumen test',
        componentes=[
            ComponenteAWS(
                servicio='Lambda',
                rol='API',
                supuesto='1M req',
                millones_peticiones=1.0,
            ),
        ],
    )
    estimacion = EstimadoCostoAWS(
        items=[],
        total_mensual=50.0,
        total_anual=600.0,
    )
    hoja = HojaRutaAWS(
        resumen='Hoja test',
        fases=[FaseHojaRuta(titulo='Cuenta', descripcion='Crear cuenta')],
    )

    async def _run():
        with patch(
            'backend.services.orchestrator.validar_prompt',
            new_callable=AsyncMock,
            return_value=ValidacionPrompt(
                es_relevante=True,
                categoria='problema_negocio',
                mensaje='',
            ),
        ):
            sesion.arquitecto.run = AsyncMock(return_value=_run_output(arquitectura))
            sesion.calculador.run = AsyncMock(return_value=_run_output(estimacion))
            sesion.roadmap_agent.run = AsyncMock(return_value=_run_output(hoja))
            return await procesar_consulta(sesion, 'Necesito una app sencilla')

    result = asyncio.run(_run())
    assert result.ok
    assert result.propuesta is not None
    assert result.propuesta.cumple_presupuesto is True
    assert result.estimacion.total_mensual == 50.0


def test_procesar_consulta_no_relevante():
    sesion = _sesion_mock()

    async def _run():
        with patch(
            'backend.services.orchestrator.validar_prompt',
            new_callable=AsyncMock,
            return_value=ValidacionPrompt(
                es_relevante=False,
                categoria='off_topic',
                mensaje='Fuera de tema',
            ),
        ):
            return await procesar_consulta(sesion, 'cuéntame un chiste')

    result = asyncio.run(_run())
    assert not result.ok
    assert result.advertencia == 'Fuera de tema'
