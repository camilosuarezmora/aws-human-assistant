"""Resolución de precios EC2/RDS: caché + API AWS + fallback estático."""

from __future__ import annotations

import logging

from backend import pricing as static_pricing
from backend.aws_pricing_client import (
    SERVICE_EC2,
    SERVICE_RDS,
    filtros_ec2,
    filtros_rds,
    precio_on_demand_hora,
)
from backend.config import (
    DEFAULT_REGION,
    aws_pricing_enabled,
    pricing_cache_ttl_seconds,
)
from backend.pricing_cache import PricingCache, make_cache_key

logger = logging.getLogger(__name__)

HORAS_MES = 730

_cache: PricingCache | None = None


def _get_cache() -> PricingCache:
    global _cache
    if _cache is None:
        _cache = PricingCache(pricing_cache_ttl_seconds())
    return _cache


def reset_cache_for_tests() -> None:
    """Limpia la caché global (solo para tests)."""
    global _cache
    if _cache is not None:
        _cache.clear()
    _cache = None


def _should_call_api() -> bool:
    return aws_pricing_enabled()


def _fallback_ec2_hora(tipo_instancia: str, region: str) -> float:
    """Precio hora desde tablas estáticas (solo us-east-1 catalogado)."""
    if region != DEFAULT_REGION:
        logger.debug(
            'Fallback estático EC2 para región %s (tabla es %s)',
            region,
            DEFAULT_REGION,
        )
    mensual = static_pricing.PRECIOS_EC2_US_EAST_1.get(tipo_instancia.lower(), 0.05)
    return mensual / HORAS_MES


def _fallback_rds_hora(tipo_instancia: str, region: str) -> float:
    if region != DEFAULT_REGION:
        logger.debug(
            'Fallback estático RDS para región %s (tabla es %s)',
            region,
            DEFAULT_REGION,
        )
    mensual = static_pricing.PRECIOS_RDS_US_EAST_1.get(tipo_instancia.lower(), 0.05)
    return mensual / HORAS_MES


def precio_ec2_hora(tipo_instancia: str, region: str = DEFAULT_REGION) -> float:
    """USD/hora On-Demand Linux para EC2."""
    tipo = tipo_instancia.lower()
    region = region.lower()
    key = make_cache_key(SERVICE_EC2, region, tipo)
    cached = _get_cache().get(key)
    if cached is not None:
        return float(cached)

    precio: float | None = None
    if _should_call_api():
        precio = precio_on_demand_hora(SERVICE_EC2, filtros_ec2(tipo, region))

    if precio is None:
        precio = _fallback_ec2_hora(tipo, region)
    else:
        logger.debug('EC2 %s @ %s desde API: $%.6f/h', tipo, region, precio)

    _get_cache().set(key, precio)
    return precio


def precio_ec2_mensual(tipo_instancia: str, region: str = DEFAULT_REGION) -> float:
    return precio_ec2_hora(tipo_instancia, region) * HORAS_MES


def precio_rds_hora(
    tipo_instancia: str,
    region: str = DEFAULT_REGION,
    *,
    database_engine: str = 'MySQL',
    deployment_option: str = 'Single-AZ',
) -> float:
    """USD/hora On-Demand para instancia RDS (compute)."""
    tipo = tipo_instancia.lower()
    region = region.lower()
    key = make_cache_key(SERVICE_RDS, region, tipo, database_engine, deployment_option)
    cached = _get_cache().get(key)
    if cached is not None:
        return float(cached)

    precio: float | None = None
    if _should_call_api():
        precio = precio_on_demand_hora(
            SERVICE_RDS,
            filtros_rds(
                tipo,
                region,
                database_engine=database_engine,
                deployment_option=deployment_option,
            ),
        )

    if precio is None:
        precio = _fallback_rds_hora(tipo, region)
    else:
        logger.debug('RDS %s @ %s desde API: $%.6f/h', tipo, region, precio)

    _get_cache().set(key, precio)
    return precio


def precio_rds_mensual(
    tipo_instancia: str,
    region: str = DEFAULT_REGION,
    *,
    database_engine: str = 'MySQL',
    deployment_option: str = 'Single-AZ',
) -> float:
    return precio_rds_hora(
        tipo_instancia,
        region,
        database_engine=database_engine,
        deployment_option=deployment_option,
    ) * HORAS_MES
