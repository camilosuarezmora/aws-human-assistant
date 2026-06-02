import os
from unittest.mock import patch

import pytest

from backend import pricing as static_pricing
from backend.pricing_resolver import HORAS_MES, precio_ec2_hora, precio_ec2_mensual


def test_precio_ec2_mensual_es_hora_por_730():
    with patch('backend.pricing_resolver._should_call_api', return_value=False):
        hora = precio_ec2_hora('t3.micro', 'us-east-1')
        mensual = precio_ec2_mensual('t3.micro', 'us-east-1')
    assert mensual == pytest.approx(hora * HORAS_MES)


def test_fallback_ec2_usa_tabla_estatica():
    with patch('backend.pricing_resolver._should_call_api', return_value=False):
        hora = precio_ec2_hora('t3.micro', 'us-east-1')
    esperado = static_pricing.PRECIOS_EC2_US_EAST_1['t3.micro'] / HORAS_MES
    assert hora == pytest.approx(esperado)


def test_api_ec2_cachea_segunda_llamada():
    with patch('backend.pricing_resolver._should_call_api', return_value=True):
        with patch(
            'backend.pricing_resolver.precio_on_demand_hora',
            return_value=0.0104,
        ) as mock_api:
            hora1 = precio_ec2_hora('t3.micro', 'us-east-1')
            hora2 = precio_ec2_hora('t3.micro', 'us-east-1')

    assert hora1 == 0.0104
    assert hora2 == 0.0104
    assert mock_api.call_count == 1


def test_api_falla_usa_fallback():
    with patch('backend.pricing_resolver._should_call_api', return_value=True):
        with patch('backend.pricing_resolver.precio_on_demand_hora', return_value=None):
            hora = precio_ec2_hora('t3.micro', 'us-east-1')

    esperado = static_pricing.PRECIOS_EC2_US_EAST_1['t3.micro'] / HORAS_MES
    assert hora == pytest.approx(esperado)


@pytest.mark.integration
def test_live_ec2_t3_micro_us_east_1():
    if not os.getenv('AWS_ACCESS_KEY_ID') and not os.path.exists(
        os.path.expanduser('~/.aws/credentials')
    ):
        pytest.skip('Sin credenciales AWS')
    with patch('backend.pricing_resolver._should_call_api', return_value=True):
        hora = precio_ec2_hora('t3.micro', 'us-east-1')
    assert hora > 0
