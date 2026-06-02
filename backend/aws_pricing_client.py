"""Cliente AWS Price List Query API (boto3 pricing)."""

from __future__ import annotations

import json
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from backend.config import pricing_api_region

logger = logging.getLogger(__name__)

SERVICE_EC2 = 'AmazonEC2'
SERVICE_RDS = 'AmazonRDS'

Filter = dict[str, str]


def _term_match(field: str, value: str) -> Filter:
    return {'Type': 'TERM_MATCH', 'Field': field, 'Value': value}


def filtros_ec2(instance_type: str, region_code: str) -> list[Filter]:
    """Filtros On-Demand Linux shared tenancy para una instancia EC2."""
    return [
        _term_match('regionCode', region_code),
        _term_match('instanceType', instance_type),
        _term_match('operatingSystem', 'Linux'),
        _term_match('tenancy', 'Shared'),
        _term_match('capacitystatus', 'Used'),
        _term_match('marketoption', 'OnDemand'),
        _term_match('preInstalledSw', 'NA'),
    ]


def filtros_rds(
    db_instance_class: str,
    region_code: str,
    *,
    database_engine: str = 'MySQL',
    deployment_option: str = 'Single-AZ',
) -> list[Filter]:
    """Filtros RDS On-Demand (motor y despliegue por defecto documentados en README)."""
    return [
        _term_match('regionCode', region_code),
        _term_match('instanceType', db_instance_class),
        _term_match('databaseEngine', database_engine),
        _term_match('deploymentOption', deployment_option),
        _term_match('licenseModel', 'No license required'),
    ]


def crear_cliente_pricing():
    """Crea cliente boto3 pricing en la región de endpoint configurada."""
    return boto3.client('pricing', region_name=pricing_api_region())


def extraer_precio_on_demand_usd(product: dict[str, Any]) -> float | None:
    """Extrae USD/hora del primer price dimension On-Demand del producto."""
    on_demand = product.get('terms', {}).get('OnDemand', {})
    if not on_demand:
        return None
    for term in on_demand.values():
        for dimension in term.get('priceDimensions', {}).values():
            usd = dimension.get('pricePerUnit', {}).get('USD')
            if usd is not None:
                return float(usd)
    return None


def get_products(
    service_code: str,
    filters: list[Filter],
    *,
    client=None,
    max_results: int = 1,
) -> list[dict[str, Any]]:
    """
    Consulta GetProducts y devuelve productos parseados.
    Devuelve lista vacía si no hay resultados o falla la API.
    """
    if client is None:
        client = crear_cliente_pricing()
    try:
        response = client.get_products(
            ServiceCode=service_code,
            Filters=filters,
            FormatVersion='aws_v1',
            MaxResults=max_results,
        )
    except (ClientError, BotoCoreError, NoCredentialsError) as exc:
        logger.warning('AWS Pricing API error (%s): %s', service_code, exc)
        return []

    products: list[dict[str, Any]] = []
    for raw in response.get('PriceList', []):
        try:
            products.append(json.loads(raw))
        except json.JSONDecodeError:
            logger.warning('PriceList entry is not valid JSON for %s', service_code)
    return products


def precio_on_demand_hora(
    service_code: str,
    filters: list[Filter],
    *,
    client=None,
) -> float | None:
    """Obtiene USD/hora On-Demand para el primer SKU que coincida con los filtros."""
    products = get_products(service_code, filters, client=client, max_results=1)
    if not products:
        return None
    return extraer_precio_on_demand_usd(products[0])
