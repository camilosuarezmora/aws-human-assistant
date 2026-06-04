"""Validación de modelos y fixtures de negocio."""

import json
from pathlib import Path

import pytest

from backend.models import ContextoNegocio, PropuestaCompletaAWS

FIXTURES = Path(__file__).parent / 'fixtures'


@pytest.fixture
def contexto_ecommerce() -> ContextoNegocio:
    data = json.loads((FIXTURES / 'contexto_ecommerce.json').read_text(encoding='utf-8'))
    return ContextoNegocio.model_validate(data)


def test_contexto_ecommerce_fixture(contexto_ecommerce: ContextoNegocio):
    assert contexto_ecommerce.presupuesto_mensual_usd == 200.0
    assert 'servidores' in contexto_ecommerce.restricciones[0]


@pytest.mark.parametrize(
    'fixture_name',
    ['contexto_ecommerce.json', 'contexto_blog.json', 'contexto_saas.json'],
)
def test_contextos_negocio_fixtures(fixture_name: str):
    data = json.loads((FIXTURES / fixture_name).read_text(encoding='utf-8'))
    ctx = ContextoNegocio.model_validate(data)
    assert ctx.problema
    assert ctx.tipo_negocio


def test_propuesta_completa_estructura():
    data = json.loads((FIXTURES / 'propuesta_estructura.json').read_text(encoding='utf-8'))
    prop = PropuestaCompletaAWS.model_validate(data)
    assert prop.estimacion.total_mensual == 2.0
    assert len(prop.arquitectura.componentes) == 2
    assert prop.cumple_presupuesto is True
