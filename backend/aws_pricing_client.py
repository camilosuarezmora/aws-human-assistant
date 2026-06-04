"""Cliente AWS Price List Query API (boto3 pricing)."""

from __future__ import annotations

import json
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from backend.config import pricing_api_region
from backend.pricing_exceptions import PricingUnavailableError

logger = logging.getLogger(__name__)

SERVICE_EC2 = 'AmazonEC2'
SERVICE_RDS = 'AmazonRDS'
SERVICE_ELASTICACHE = 'AmazonElastiCache'
SERVICE_S3 = 'AmazonS3'
SERVICE_LAMBDA = 'AWSLambda'
SERVICE_DYNAMODB = 'AmazonDynamoDB'
SERVICE_API_GATEWAY = 'AmazonApiGateway'
SERVICE_SNS = 'AmazonSNS'
SERVICE_SQS = 'AmazonSQS'
SERVICE_ELB = 'AWSELB'
SERVICE_CLOUDFRONT = 'AmazonCloudFront'
SERVICE_ROUTE53 = 'AmazonRoute53'
SERVICE_ECS = 'AmazonECS'
SERVICE_COGNITO = 'AmazonCognito'
SERVICE_CLOUDWATCH = 'AmazonCloudWatch'
SERVICE_VPC = 'AmazonVPC'

Filter = dict[str, str]

FUENTE_PRECIO = 'AWS Price List API'


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
    """Filtros RDS On-Demand (compute)."""
    return [
        _term_match('regionCode', region_code),
        _term_match('instanceType', db_instance_class),
        _term_match('databaseEngine', database_engine),
        _term_match('deploymentOption', deployment_option),
        _term_match('licenseModel', 'No license required'),
    ]


def filtros_rds_storage(region_code: str, *, database_engine: str = 'MySQL') -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'Database Storage'),
        _term_match('databaseEngine', database_engine),
        _term_match('storageMedia', 'General Purpose'),
    ]


def filtros_elasticache(
    instance_type: str,
    region_code: str,
    *,
    cache_engine: str = 'Redis',
) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('instanceType', instance_type),
        _term_match('cacheEngine', cache_engine),
        _term_match('locationType', 'AWS Region'),
    ]


def filtros_s3_standard(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('storageClass', 'General Purpose'),
        _term_match('volumeType', 'Standard'),
        _term_match('locationType', 'AWS Region'),
    ]


def filtros_transferencia_saliente(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'Data Transfer'),
        _term_match('transferType', 'Data Transfer Outbound'),
        _term_match('fromRegionCode', region_code),
        _term_match('toLocation', 'External'),
    ]


def filtros_lambda_requests(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('group', 'AWS-Lambda-Requests'),
    ]


def filtros_lambda_duration(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('group', 'AWS-Lambda-Duration'),
    ]


def filtros_dynamodb_write(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('group', 'DDB-WriteUnits'),
    ]


def filtros_dynamodb_read(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('group', 'DDB-ReadUnits'),
    ]


def filtros_api_gateway_rest(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'API calls'),
        _term_match('apiType', 'REST'),
    ]


def filtros_sns(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'API Request'),
    ]


def filtros_sqs(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'API Request'),
    ]


def filtros_alb(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'Load Balancer-Application'),
    ]


def filtros_cloudfront_transferencia() -> list[Filter]:
    return [
        _term_match('productFamily', 'Data Transfer'),
        _term_match('transferType', 'Data Transfer Out'),
        _term_match('location', 'United States'),
    ]


def filtros_route53_hosted_zone() -> list[Filter]:
    return [
        _term_match('productFamily', 'DNS Zone'),
        _term_match('routingType', 'Public'),
    ]


def filtros_fargate_vcpu(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('launchType', 'FARGATE'),
        _term_match('productFamily', 'Compute'),
        _term_match('resource', 'vCPU'),
    ]


def filtros_fargate_memoria(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('launchType', 'FARGATE'),
        _term_match('productFamily', 'Compute'),
        _term_match('resource', 'Memory'),
    ]


def filtros_ecs_cluster(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'Compute'),
        _term_match('launchType', 'EC2'),
    ]


def filtros_cognito_mau(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'User Pools'),
        _term_match('group', 'CognitoUserPoolsMAU'),
    ]


def filtros_cloudwatch_logs(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'Data Processing'),
        _term_match('group', 'CW:Logs'),
    ]


def filtros_nat_gateway(region_code: str) -> list[Filter]:
    return [
        _term_match('regionCode', region_code),
        _term_match('productFamily', 'NAT Gateway'),
    ]


def crear_cliente_pricing():
    """Crea cliente boto3 pricing en la región de endpoint configurada."""
    return boto3.client('pricing', region_name=pricing_api_region())


def extraer_precio_on_demand_usd(product: dict[str, Any]) -> float | None:
    """Extrae USD/hora del primer price dimension On-Demand (compatibilidad tests)."""
    return extraer_precio_usd(product, units=('Hrs',))


def extraer_precio_usd(
    product: dict[str, Any],
    *,
    units: tuple[str, ...] | None = None,
) -> float | None:
    """Extrae el primer precio USD On-Demand, opcionalmente filtrado por unidad."""
    on_demand = product.get('terms', {}).get('OnDemand', {})
    if not on_demand:
        return None
    for term in on_demand.values():
        for dimension in term.get('priceDimensions', {}).values():
            unit = dimension.get('unit', '')
            if units and unit not in units:
                continue
            usd = dimension.get('pricePerUnit', {}).get('USD')
            if usd is not None:
                return float(usd)
    return None


def get_products(
    service_code: str,
    filters: list[Filter],
    *,
    client=None,
    max_results: int = 10,
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


def consultar_precio_usd(
    service_code: str,
    filters: list[Filter],
    *,
    units: tuple[str, ...] | None = None,
    client=None,
    max_results: int = 10,
) -> float | None:
    """Devuelve el primer precio USD que coincida con filtros y unidades opcionales."""
    products = get_products(
        service_code,
        filters,
        client=client,
        max_results=max_results,
    )
    for product in products:
        precio = extraer_precio_usd(product, units=units)
        if precio is not None:
            return precio
    return None


def precio_on_demand_hora(
    service_code: str,
    filters: list[Filter],
    *,
    client=None,
) -> float | None:
    """Obtiene USD/hora On-Demand para el primer SKU que coincida."""
    return consultar_precio_usd(service_code, filters, units=('Hrs',), client=client)


def requerir_precio_usd(
    service_code: str,
    filters: list[Filter],
    *,
    servicio: str,
    region: str | None = None,
    units: tuple[str, ...] | None = None,
    client=None,
    max_results: int = 10,
) -> float:
    """Consulta la API y lanza PricingUnavailableError si no hay precio."""
    precio = consultar_precio_usd(
        service_code,
        filters,
        units=units,
        client=client,
        max_results=max_results,
    )
    if precio is None:
        raise PricingUnavailableError(
            servicio=servicio,
            region=region,
            detalle=f'serviceCode={service_code}, filtros={len(filters)}',
        )
    return precio
