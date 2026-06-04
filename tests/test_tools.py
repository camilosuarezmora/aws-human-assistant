"""Tests unitarios de herramientas de costos."""

from unittest.mock import patch

import pytest

from backend.tools import (
    costo_alb,
    costo_cloudfront,
    costo_cognito,
    costo_fargate,
    costo_nat_gateway,
    costo_route53,
    obtener_fuente_precio,
)


def test_costo_alb():
    with patch('backend.tools.precio_alb_mensual', return_value=22.5):
        item = costo_alb(2)
    assert item.servicio == 'ALB'
    assert item.costo_total_mensual == 45.0
    assert item.cantidad == 2


def test_costo_cloudfront():
    with patch('backend.tools.precio_cloudfront_gb', return_value=0.085):
        item = costo_cloudfront(100)
    assert item.servicio == 'CloudFront'
    assert item.costo_total_mensual == pytest.approx(8.5)


def test_costo_route53():
    with patch('backend.tools.precio_route53_hosted_zone_mes', return_value=0.5):
        item = costo_route53(2)
    assert item.cantidad == 2
    assert item.costo_total_mensual == 1.0


def test_costo_fargate():
    with (
        patch('backend.tools.precio_fargate_vcpu_hora', return_value=0.04),
        patch('backend.tools.precio_fargate_gb_hora', return_value=0.004),
    ):
        item = costo_fargate(vcpu=0.5, memoria_gb=1.0, horas_mes=100)
    assert item.servicio == 'Fargate'
    assert item.costo_total_mensual > 0


def test_costo_cognito():
    with patch('backend.tools.precio_cognito_por_mau', return_value=0.0055):
        item = costo_cognito(10_000)
    assert item.costo_total_mensual == pytest.approx(55.0)


def test_costo_nat_gateway():
    with patch('backend.tools.precio_nat_gateway_mensual', return_value=32.4):
        item = costo_nat_gateway(1)
    assert item.costo_total_mensual == 32.4


def test_obtener_fuente_precio():
    texto = obtener_fuente_precio('EC2')
    assert 'AWS Price List API' in texto
    assert 'estática' not in texto.lower()
