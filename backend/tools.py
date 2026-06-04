"""Herramientas de cálculo de costos expuestas al agente."""

from backend.models import CostoItem
from backend import pricing as p
from backend.pricing_resolver import precio_ec2_mensual, precio_rds_mensual


def costo_ec2(tipo_instancia: str, cantidad: int = 1, region: str = 'us-east-1') -> CostoItem:
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
    region: str = 'us-east-1',
) -> CostoItem:
    """Calcula costo de RDS (base de datos gestionada)."""
    precio_instancia = precio_rds_mensual(tipo_instancia, region)
    costo_instancia = precio_instancia * cantidad
    costo_storage = p.PRECIO_RDS_STORAGE_POR_GB * storage_gb * cantidad
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


def costo_elasticache(tipo_instancia: str, cantidad: int = 1) -> CostoItem:
    """Calcula costo de ElastiCache (Redis/Memcached)."""
    precio = p.PRECIOS_ELASTICACHE.get(tipo_instancia.lower(), 0.024)
    costo_total = precio * cantidad
    return CostoItem(
        servicio='ElastiCache',
        descripcion=f'{cantidad} nodo(s) {tipo_instancia}',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_s3(almacenamiento_gb: float) -> CostoItem:
    """Calcula costo de S3 (almacenamiento de objetos)."""
    costo_total = almacenamiento_gb * p.PRECIO_S3_POR_GB
    return CostoItem(
        servicio='S3',
        descripcion=f'{almacenamiento_gb}GB de almacenamiento S3 Standard',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_transferencia_datos(gb_salientes: float) -> CostoItem:
    """Calcula costo de transferencia de datos saliente."""
    costo_total = gb_salientes * p.PRECIO_TRANSFERENCIA_POR_GB
    return CostoItem(
        servicio='Transferencia de Datos',
        descripcion=f'{gb_salientes}GB de transferencia saliente',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_lambda(millones_peticiones: float = 0, gb_segundos: float = 0) -> CostoItem:
    """Calcula costo de AWS Lambda."""
    costo_total = (
        millones_peticiones * p.PRECIO_LAMBDA_POR_MILLON_REQ
        + gb_segundos * p.PRECIO_LAMBDA_POR_GB_SEGUNDO
    )
    return CostoItem(
        servicio='Lambda',
        descripcion=f'{millones_peticiones}M peticiones, {gb_segundos}GB-segundos',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_api_gateway(millones_peticiones: float) -> CostoItem:
    """Calcula costo de API Gateway."""
    costo_total = millones_peticiones * p.PRECIO_API_GATEWAY_POR_MILLON
    return CostoItem(
        servicio='API Gateway',
        descripcion=f'{millones_peticiones}M peticiones API REST',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_dynamodb(millones_escrituras: float = 0, millones_lecturas: float = 0) -> CostoItem:
    """Calcula costo de DynamoDB."""
    costo_total = (
        millones_escrituras * p.PRECIO_DYNAMODB_ESCRITURA
        + millones_lecturas * p.PRECIO_DYNAMODB_LECTURA
    )
    return CostoItem(
        servicio='DynamoDB',
        descripcion=f'{millones_escrituras}M escrituras, {millones_lecturas}M lecturas',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_sns(millones_peticiones: float) -> CostoItem:
    """Calcula costo de SNS (Simple Notification Service)."""
    costo_total = millones_peticiones * p.PRECIO_SNS_POR_MILLON
    return CostoItem(
        servicio='SNS',
        descripcion=f'{millones_peticiones}M notificaciones',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_sqs(millones_peticiones: float) -> CostoItem:
    """Calcula costo de SQS (Simple Queue Service)."""
    costo_total = millones_peticiones * p.PRECIO_SQS_POR_MILLON
    return CostoItem(
        servicio='SQS',
        descripcion=f'{millones_peticiones}M mensajes en cola',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_alb(cantidad: int = 1) -> CostoItem:
    """Calcula costo de Application Load Balancer (tarifa base mensual referencia)."""
    precio = p.PRECIO_ALB_MENSUAL
    costo_total = precio * cantidad
    return CostoItem(
        servicio='ALB',
        descripcion=f'{cantidad} Application Load Balancer(es)',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_cloudfront(gb_salientes: float) -> CostoItem:
    """Calcula costo de CloudFront por GB transferido (estimación)."""
    costo_total = gb_salientes * p.PRECIO_CLOUDFRONT_POR_GB
    return CostoItem(
        servicio='CloudFront',
        descripcion=f'{gb_salientes}GB transferidos vía CDN',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_route53(hosted_zones: int = 1) -> CostoItem:
    """Calcula costo de Route 53 hosted zones."""
    precio = p.PRECIO_ROUTE53_HOSTED_ZONE_MENSUAL
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
    horas_mes: float = 730,
) -> CostoItem:
    """Calcula costo de AWS Fargate (vCPU y memoria por hora)."""
    costo_hora = (
        vcpu * p.PRECIO_FARGATE_VCPU_HORA + memoria_gb * p.PRECIO_FARGATE_GB_HORA
    )
    costo_total = costo_hora * horas_mes
    return CostoItem(
        servicio='Fargate',
        descripcion=f'Fargate {vcpu} vCPU, {memoria_gb}GB RAM, {horas_mes}h/mes',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_ecs(cantidad: int = 1) -> CostoItem:
    """Calcula costo referencia de cluster ECS pequeño (sin Fargate incluido)."""
    precio = p.PRECIO_ECS_CLUSTER_REF_MENSUAL
    costo_total = precio * cantidad
    return CostoItem(
        servicio='ECS',
        descripcion=f'{cantidad} cluster(s) ECS (tarifa control plan referencia)',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_cognito(usuarios_mau: int = 1000) -> CostoItem:
    """Calcula costo de Amazon Cognito por usuarios activos mensuales."""
    costo_total = usuarios_mau * p.PRECIO_COGNITO_POR_MAU
    return CostoItem(
        servicio='Cognito',
        descripcion=f'{usuarios_mau} usuarios activos mensuales (MAU)',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_cloudwatch(gb_logs: float = 5) -> CostoItem:
    """Calcula costo de CloudWatch Logs por GB ingerido."""
    costo_total = gb_logs * p.PRECIO_CLOUDWATCH_LOG_POR_GB
    return CostoItem(
        servicio='CloudWatch',
        descripcion=f'{gb_logs}GB de logs ingeridos',
        cantidad=1,
        costo_unitario_mensual=costo_total,
        costo_total_mensual=costo_total,
    )


def costo_nat_gateway(cantidad: int = 1) -> CostoItem:
    """Calcula costo de NAT Gateway (tarifa base mensual referencia)."""
    precio = p.PRECIO_NAT_GATEWAY_MENSUAL
    costo_total = precio * cantidad
    return CostoItem(
        servicio='NAT Gateway',
        descripcion=f'{cantidad} NAT Gateway(s)',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def obtener_fuente_precio(servicio: str) -> str:
    """Indica si el servicio usa API AWS en vivo o tabla estática."""
    if servicio.upper() in ('EC2', 'RDS'):
        return (
            f'{servicio}: AWS Price List API si está habilitada, '
            f'si no tabla {p.FECHA_PRECIOS_ESTATICOS}'
        )
    return f'{servicio}: tabla estática {p.FECHA_PRECIOS_ESTATICOS}'


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
