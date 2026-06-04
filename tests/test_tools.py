"""Tests unitarios de herramientas de costos."""

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
    item = costo_alb(2)
    assert item.servicio == 'ALB'
    assert item.costo_total_mensual > 0
    assert item.cantidad == 2


def test_costo_cloudfront():
    item = costo_cloudfront(100)
    assert item.servicio == 'CloudFront'
    assert item.costo_total_mensual > 0


def test_costo_route53():
    item = costo_route53(2)
    assert item.cantidad == 2


def test_costo_fargate():
    item = costo_fargate(vcpu=0.5, memoria_gb=1.0, horas_mes=100)
    assert item.servicio == 'Fargate'
    assert item.costo_total_mensual > 0


def test_costo_cognito():
    item = costo_cognito(10_000)
    assert item.costo_total_mensual > 0


def test_costo_nat_gateway():
    item = costo_nat_gateway(1)
    assert item.costo_total_mensual > 0


def test_obtener_fuente_precio():
    assert 'API' in obtener_fuente_precio('EC2') or 'tabla' in obtener_fuente_precio('EC2')
    assert 'estática' in obtener_fuente_precio('ALB')
