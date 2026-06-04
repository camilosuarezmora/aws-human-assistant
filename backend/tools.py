"""Herramientas de cálculo de costos expuestas al agente (precios solo vía API AWS)."""

from backend.config import DEFAULT_REGION
from backend.models import CostoItem
from backend.pricing_resolver import (
    FUENTE_PRECIO,
    HORAS_MES,
    precio_alb_mensual,
    precio_api_gateway_por_millon,
    precio_cloudfront_gb,
    precio_cloudwatch_logs_gb,
    precio_cognito_por_mau,
    precio_dynamodb_escritura_millon,
    precio_dynamodb_lectura_millon,
    precio_ec2_mensual,
    precio_ecs_cluster_mes,
    precio_elasticache_mensual,
    precio_fargate_gb_hora,
    precio_fargate_vcpu_hora,
    precio_lambda_gb_segundo,
    precio_lambda_por_millon_requests,
    precio_nat_gateway_mensual,
    precio_rds_mensual,
    precio_rds_storage_gb_mes,
    precio_route53_hosted_zone_mes,
    precio_s3_gb_mes,
    precio_sns_por_millon,
    precio_sqs_por_millon,
    precio_transferencia_gb,
)


def costo_ec2(tipo_instancia: str, cantidad: int = 1, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo de instancias EC2."""
    precio = precio_ec2_mensual(tipo_instancia, region)
    costo_total = precio * cantidad
    return CostoItem(
        servicio='EC2',
        descripcion=f'{cantidad} instancia(s) {tipo_instancia} ({region})',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_rds(
    tipo_instancia: str,
    cantidad: int = 1,
    storage_gb: int = 20,
    region: str = DEFAULT_REGION,
) -> CostoItem:
    """Calcula costo de RDS (base de datos gestionada)."""
    precio_instancia = precio_rds_mensual(tipo_instancia, region)
    precio_storage = precio_rds_storage_gb_mes(region)
    costo_instancia = precio_instancia * cantidad
    costo_storage = precio_storage * storage_gb * cantidad
    costo_total = costo_instancia + costo_storage
    return CostoItem(
        servicio='RDS',
        descripcion=(
            f'{cantidad} instancia(s) {tipo_instancia} con {storage_gb}GB storage ({region})'
        ),
        cantidad=cantidad,
        costo_unitario_mensual=costo_total / cantidad,
        costo_total_mensual=costo_total,
    )


def costo_elasticache(
    tipo_instancia: str,
    cantidad: int = 1,
    region: str = DEFAULT_REGION,
) -> CostoItem:
    """Calcula costo de ElastiCache (Redis/Memcached)."""
    precio = precio_elasticache_mensual(tipo_instancia, region)
    costo_total = precio * cantidad
    return CostoItem(
        servicio='ElastiCache',
        descripcion=f'{cantidad} nodo(s) {tipo_instancia} ({region})',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_s3(almacenamiento_gb: float, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo de S3 (almacenamiento de objetos)."""
    precio_gb = precio_s3_gb_mes(region)
    costo_total = almacenamiento_gb * precio_gb
    return CostoItem(
        servicio='S3',
        descripcion=f'{almacenamiento_gb}GB de almacenamiento S3 Standard ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_transferencia_datos(
    gb_salientes: float,
    region: str = DEFAULT_REGION,
) -> CostoItem:
    """Calcula costo de transferencia de datos saliente."""
    precio_gb = precio_transferencia_gb(region)
    costo_total = gb_salientes * precio_gb
    return CostoItem(
        servicio='Transferencia de Datos',
        descripcion=f'{gb_salientes}GB de transferencia saliente ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_lambda(
    millones_peticiones: float = 0,
    gb_segundos: float = 0,
    region: str = DEFAULT_REGION,
) -> CostoItem:
    """Calcula costo de AWS Lambda."""
    precio_req = precio_lambda_por_millon_requests(region)
    precio_gb_s = precio_lambda_gb_segundo(region)
    costo_total = (
        millones_peticiones * precio_req + gb_segundos * precio_gb_s
    )
    return CostoItem(
        servicio='Lambda',
        descripcion=f'{millones_peticiones}M peticiones, {gb_segundos}GB-segundos ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_api_gateway(
    millones_peticiones: float,
    region: str = DEFAULT_REGION,
) -> CostoItem:
    """Calcula costo de API Gateway."""
    precio = precio_api_gateway_por_millon(region)
    costo_total = millones_peticiones * precio
    return CostoItem(
        servicio='API Gateway',
        descripcion=f'{millones_peticiones}M peticiones API REST ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_dynamodb(
    millones_escrituras: float = 0,
    millones_lecturas: float = 0,
    region: str = DEFAULT_REGION,
) -> CostoItem:
    """Calcula costo de DynamoDB."""
    precio_w = precio_dynamodb_escritura_millon(region)
    precio_r = precio_dynamodb_lectura_millon(region)
    costo_total = millones_escrituras * precio_w + millones_lecturas * precio_r
    return CostoItem(
        servicio='DynamoDB',
        descripcion=(
            f'{millones_escrituras}M escrituras, {millones_lecturas}M lecturas ({region})'
        ),
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_sns(millones_peticiones: float, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo de SNS (Simple Notification Service)."""
    precio = precio_sns_por_millon(region)
    costo_total = millones_peticiones * precio
    return CostoItem(
        servicio='SNS',
        descripcion=f'{millones_peticiones}M notificaciones ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_sqs(millones_peticiones: float, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo de SQS (Simple Queue Service)."""
    precio = precio_sqs_por_millon(region)
    costo_total = millones_peticiones * precio
    return CostoItem(
        servicio='SQS',
        descripcion=f'{millones_peticiones}M mensajes en cola ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_alb(cantidad: int = 1, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo de Application Load Balancer (tarifa base mensual desde API)."""
    precio = precio_alb_mensual(region)
    costo_total = precio * cantidad
    return CostoItem(
        servicio='ALB',
        descripcion=f'{cantidad} Application Load Balancer(es) ({region})',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_cloudfront(gb_salientes: float) -> CostoItem:
    """Calcula costo de CloudFront por GB transferido."""
    precio_gb = precio_cloudfront_gb()
    costo_total = gb_salientes * precio_gb
    return CostoItem(
        servicio='CloudFront',
        descripcion=f'{gb_salientes}GB transferidos vía CDN',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_route53(hosted_zones: int = 1) -> CostoItem:
    """Calcula costo de Route 53 hosted zones."""
    precio = precio_route53_hosted_zone_mes()
    costo_total = precio * hosted_zones
    return CostoItem(
        servicio='Route53',
        descripcion=f'{hosted_zones} hosted zone(s) DNS',
        cantidad=hosted_zones,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_fargate(
    vcpu: float = 0.25,
    memoria_gb: float = 0.5,
    horas_mes: float = HORAS_MES,
    region: str = DEFAULT_REGION,
) -> CostoItem:
    """Calcula costo de AWS Fargate (vCPU y memoria por hora)."""
    costo_hora = (
        vcpu * precio_fargate_vcpu_hora(region)
        + memoria_gb * precio_fargate_gb_hora(region)
    )
    costo_total = costo_hora * horas_mes
    return CostoItem(
        servicio='Fargate',
        descripcion=f'Fargate {vcpu} vCPU, {memoria_gb}GB RAM, {horas_mes}h/mes ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_ecs(cantidad: int = 1, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo del plano de control ECS desde API."""
    precio = precio_ecs_cluster_mes(region)
    costo_total = precio * cantidad
    return CostoItem(
        servicio='ECS',
        descripcion=f'{cantidad} cluster(s) ECS ({region})',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_cognito(usuarios_mau: int = 1000, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo de Amazon Cognito por usuarios activos mensuales."""
    precio_mau = precio_cognito_por_mau(region)
    costo_total = usuarios_mau * precio_mau
    return CostoItem(
        servicio='Cognito',
        descripcion=f'{usuarios_mau} usuarios activos mensuales (MAU) ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_cloudwatch(gb_logs: float = 5, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo de CloudWatch Logs por GB ingerido."""
    precio_gb = precio_cloudwatch_logs_gb(region)
    costo_total = gb_logs * precio_gb
    return CostoItem(
        servicio='CloudWatch',
        descripcion=f'{gb_logs}GB de logs ingeridos ({region})',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_nat_gateway(cantidad: int = 1, region: str = DEFAULT_REGION) -> CostoItem:
    """Calcula costo de NAT Gateway (tarifa base mensual desde API)."""
    precio = precio_nat_gateway_mensual(region)
    costo_total = precio * cantidad
    return CostoItem(
        servicio='NAT Gateway',
        descripcion=f'{cantidad} NAT Gateway(s) ({region})',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def obtener_fuente_precio(servicio: str) -> str:
    """Indica la fuente de precios (siempre AWS Price List API)."""
    return f'{servicio}: {FUENTE_PRECIO}'


ALL_TOOLS = [
    costo_ec2,
    costo_rds,
    costo_elasticache,
    costo_s3,
    costo_transferencia_datos,
    costo_lambda,
    costo_api_gateway,
    costo_dynamodb,
    costo_sns,
    costo_sqs,
    costo_alb,
    costo_cloudfront,
    costo_route53,
    costo_fargate,
    costo_ecs,
    costo_cognito,
    costo_cloudwatch,
    costo_nat_gateway,
    obtener_fuente_precio,
]
