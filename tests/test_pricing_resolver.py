import os
from unittest.mock import patch

import pytest

from backend.pricing_exceptions import PricingUnavailableError
from backend.pricing_resolver import HORAS_MES, precio_ec2_hora, precio_ec2_mensual


def test_precio_ec2_mensual_es_hora_por_730():
    with patch('backend.pricing_resolver.api.precio_on_demand_hora', return_value=0.0104):
        hora = precio_ec2_hora('t3.micro', 'us-east-1')
        mensual = precio_ec2_mensual('t3.micro', 'us-east-1')
    assert mensual == pytest.approx(hora * HORAS_MES)


def test_api_ec2_cachea_segunda_llamada():
    with patch(
        'backend.pricing_resolver.api.precio_on_demand_hora',
        return_value=0.0104,
    ) as mock_api:
        hora1 = precio_ec2_hora('t3.micro', 'us-east-1')
        hora2 = precio_ec2_hora('t3.micro', 'us-east-1')

    assert hora1 == 0.0104
    assert hora2 == 0.0104
    assert mock_api.call_count == 1


def test_api_falla_lanza_error():
    with patch('backend.pricing_resolver.api.precio_on_demand_hora', return_value=None):
        with patch('backend.pricing_resolver.api.requerir_precio_usd') as mock_req:
            mock_req.side_effect = PricingUnavailableError(
                servicio='EC2',
                region='us-east-1',
            )
            with pytest.raises(PricingUnavailableError):
                precio_ec2_hora('t3.micro', 'us-east-1')


@pytest.mark.integration
def test_live_ec2_t3_micro_us_east_1():
    if not os.getenv('AWS_ACCESS_KEY_ID') and not os.path.exists(
        os.path.expanduser('~/.aws/credentials')
    ):
        pytest.skip('Sin credenciales AWS')
    hora = precio_ec2_hora('t3.micro', 'us-east-1')
    assert hora > 0
