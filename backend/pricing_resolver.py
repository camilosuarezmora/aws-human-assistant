"""Resolución de precios AWS: solo API + caché en memoria."""

from __future__ import annotations

import logging

from backend import aws_pricing_client as api
from backend.config import DEFAULT_REGION, pricing_cache_ttl_seconds
from backend.pricing_cache import PricingCache, make_cache_key

logger = logging.getLogger(__name__)

HORAS_MES = 730
FUENTE_PRECIO = api.FUENTE_PRECIO

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


def _cached_float(key: str, fetcher) -> float:
    cached = _get_cache().get(key)
    if cached is not None:
        return float(cached)
    precio = fetcher()
    _get_cache().set(key, precio)
    return precio


def precio_ec2_hora(tipo_instancia: str, region: str = DEFAULT_REGION) -> float:
    """USD/hora On-Demand Linux para EC2."""
    tipo = tipo_instancia.lower()
    region = region.lower()
    key = make_cache_key(api.SERVICE_EC2, region, tipo)

    def fetch() -> float:
        filtros = api.filtros_ec2(tipo, region)
        precio = api.precio_on_demand_hora(api.SERVICE_EC2, filtros)
        if precio is None:
            precio = api.requerir_precio_usd(
                api.SERVICE_EC2,
                filtros,
                servicio='EC2',
                region=region,
                units=('Hrs',),
            )
        logger.debug('EC2 %s @ %s desde API: $%.6f/h', tipo, region, precio)
        return precio

    return _cached_float(key, fetch)


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
    key = make_cache_key(
        api.SERVICE_RDS,
        region,
        tipo,
        database_engine,
        deployment_option,
    )

    def fetch() -> float:
        filtros = api.filtros_rds(
            tipo,
            region,
            database_engine=database_engine,
            deployment_option=deployment_option,
        )
        precio = api.precio_on_demand_hora(api.SERVICE_RDS, filtros)
        if precio is None:
            return api.requerir_precio_usd(
                api.SERVICE_RDS,
                filtros,
                servicio='RDS',
                region=region,
                units=('Hrs',),
            )
        logger.debug('RDS %s @ %s desde API: $%.6f/h', tipo, region, precio)
        return precio

    return _cached_float(key, fetch)


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


def precio_rds_storage_gb_mes(region: str = DEFAULT_REGION, *, database_engine: str = 'MySQL') -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_RDS, 'storage', region, database_engine)

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_RDS,
            api.filtros_rds_storage(region, database_engine=database_engine),
            servicio='RDS Storage',
            region=region,
            units=('GB-Mo',),
        )

    return _cached_float(key, fetch)


def precio_elasticache_hora(
    tipo_instancia: str,
    region: str = DEFAULT_REGION,
    *,
    cache_engine: str = 'Redis',
) -> float:
    tipo = tipo_instancia.lower()
    region = region.lower()
    key = make_cache_key(api.SERVICE_ELASTICACHE, region, tipo, cache_engine)

    def fetch() -> float:
        filtros = api.filtros_elasticache(tipo, region, cache_engine=cache_engine)
        return api.requerir_precio_usd(
            api.SERVICE_ELASTICACHE,
            filtros,
            servicio='ElastiCache',
            region=region,
            units=('Hrs',),
        )

    return _cached_float(key, fetch)


def precio_elasticache_mensual(
    tipo_instancia: str,
    region: str = DEFAULT_REGION,
    *,
    cache_engine: str = 'Redis',
) -> float:
    return precio_elasticache_hora(tipo_instancia, region, cache_engine=cache_engine) * HORAS_MES


def precio_s3_gb_mes(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_S3, region, 'standard')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_S3,
            api.filtros_s3_standard(region),
            servicio='S3',
            region=region,
            units=('GB-Mo',),
        )

    return _cached_float(key, fetch)


def precio_transferencia_gb(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_EC2, 'transfer-out', region)

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_EC2,
            api.filtros_transferencia_saliente(region),
            servicio='Transferencia de Datos',
            region=region,
            units=('GB',),
        )

    return _cached_float(key, fetch)


def precio_lambda_por_millon_requests(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_LAMBDA, region, 'requests')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_LAMBDA,
            api.filtros_lambda_requests(region),
            servicio='Lambda (peticiones)',
            region=region,
            units=('Requests',),
        )

    return _cached_float(key, fetch)


def precio_lambda_gb_segundo(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_LAMBDA, region, 'duration')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_LAMBDA,
            api.filtros_lambda_duration(region),
            servicio='Lambda (duración)',
            region=region,
            units=('Lambda-GB-Second', 'GB-Second'),
        )

    return _cached_float(key, fetch)


def precio_api_gateway_por_millon(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_API_GATEWAY, region, 'rest')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_API_GATEWAY,
            api.filtros_api_gateway_rest(region),
            servicio='API Gateway',
            region=region,
            units=('Requests',),
        )

    return _cached_float(key, fetch)


def precio_dynamodb_escritura_millon(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_DYNAMODB, region, 'write')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_DYNAMODB,
            api.filtros_dynamodb_write(region),
            servicio='DynamoDB (escrituras)',
            region=region,
            units=('WriteCapacityUnit-Hrs', 'WriteRequestUnits'),
        )

    return _cached_float(key, fetch)


def precio_dynamodb_lectura_millon(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_DYNAMODB, region, 'read')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_DYNAMODB,
            api.filtros_dynamodb_read(region),
            servicio='DynamoDB (lecturas)',
            region=region,
            units=('ReadCapacityUnit-Hrs', 'ReadRequestUnits'),
        )

    return _cached_float(key, fetch)


def precio_sns_por_millon(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_SNS, region, 'api')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_SNS,
            api.filtros_sns(region),
            servicio='SNS',
            region=region,
            units=('Requests',),
        )

    return _cached_float(key, fetch)


def precio_sqs_por_millon(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_SQS, region, 'api')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_SQS,
            api.filtros_sqs(region),
            servicio='SQS',
            region=region,
            units=('Requests',),
        )

    return _cached_float(key, fetch)


def precio_alb_hora(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_ELB, region, 'alb')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_ELB,
            api.filtros_alb(region),
            servicio='ALB',
            region=region,
            units=('Hrs',),
        )

    return _cached_float(key, fetch)


def precio_alb_mensual(region: str = DEFAULT_REGION) -> float:
    return precio_alb_hora(region) * HORAS_MES


def precio_cloudfront_gb() -> float:
    key = make_cache_key(api.SERVICE_CLOUDFRONT, 'transfer', 'us')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_CLOUDFRONT,
            api.filtros_cloudfront_transferencia(),
            servicio='CloudFront',
            region=None,
            units=('GB',),
        )

    return _cached_float(key, fetch)


def precio_route53_hosted_zone_mes() -> float:
    key = make_cache_key(api.SERVICE_ROUTE53, 'hosted-zone')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_ROUTE53,
            api.filtros_route53_hosted_zone(),
            servicio='Route53',
            region=None,
            units=('HostedZone', 'Mo'),
        )

    return _cached_float(key, fetch)


def precio_fargate_vcpu_hora(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_ECS, region, 'fargate-vcpu')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_ECS,
            api.filtros_fargate_vcpu(region),
            servicio='Fargate vCPU',
            region=region,
            units=('Hrs',),
        )

    return _cached_float(key, fetch)


def precio_fargate_gb_hora(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_ECS, region, 'fargate-mem')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_ECS,
            api.filtros_fargate_memoria(region),
            servicio='Fargate memoria',
            region=region,
            units=('Hrs',),
        )

    return _cached_float(key, fetch)


def precio_ecs_cluster_hora(region: str = DEFAULT_REGION) -> float:
    """USD/hora del plano de control ECS (si AWS publica SKU para la región)."""
    region = region.lower()
    key = make_cache_key(api.SERVICE_ECS, region, 'cluster')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_ECS,
            api.filtros_ecs_cluster(region),
            servicio='ECS',
            region=region,
            units=('Hrs',),
        )

    return _cached_float(key, fetch)


def precio_ecs_cluster_mes(region: str = DEFAULT_REGION) -> float:
    return precio_ecs_cluster_hora(region) * HORAS_MES


def precio_cognito_por_mau(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_COGNITO, region, 'mau')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_COGNITO,
            api.filtros_cognito_mau(region),
            servicio='Cognito',
            region=region,
            units=('CognitoUserPoolsMAU', 'Users'),
        )

    return _cached_float(key, fetch)


def precio_cloudwatch_logs_gb(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_CLOUDWATCH, region, 'logs')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_CLOUDWATCH,
            api.filtros_cloudwatch_logs(region),
            servicio='CloudWatch Logs',
            region=region,
            units=('GB',),
        )

    return _cached_float(key, fetch)


def precio_nat_gateway_hora(region: str = DEFAULT_REGION) -> float:
    region = region.lower()
    key = make_cache_key(api.SERVICE_VPC, region, 'nat')

    def fetch() -> float:
        return api.requerir_precio_usd(
            api.SERVICE_VPC,
            api.filtros_nat_gateway(region),
            servicio='NAT Gateway',
            region=region,
            units=('Hrs',),
        )

    return _cached_float(key, fetch)


def precio_nat_gateway_mensual(region: str = DEFAULT_REGION) -> float:
    return precio_nat_gateway_hora(region) * HORAS_MES
