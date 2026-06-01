"""Herramientas de cálculo de costos expuestas al agente."""

from aws_cost.models import CostoItem
from aws_cost import pricing as p


def costo_ec2(tipo_instancia: str, cantidad: int = 1, region: str = 'us-east-1') -> CostoItem:
    """Calcula costo de instancias EC2."""
    precio = p.PRECIOS_EC2_US_EAST_1.get(tipo_instancia.lower(), 0.05)
    costo_total = precio * cantidad
    return CostoItem(
        servicio='EC2',
        descripcion=f'{cantidad} instancia(s) {tipo_instancia} ({region})',
        cantidad=cantidad,
        costo_unitario_mensual=precio,
        costo_total_mensual=costo_total,
    )


def costo_rds(tipo_instancia: str, cantidad: int = 1, storage_gb: int = 20) -> CostoItem:
    """Calcula costo de RDS (base de datos gestionada)."""
    precio_instancia = p.PRECIOS_RDS_US_EAST_1.get(tipo_instancia.lower(), 0.05)
    costo_instancia = precio_instancia * cantidad
    costo_storage = p.PRECIO_RDS_STORAGE_POR_GB * storage_gb * cantidad
    costo_total = costo_instancia + costo_storage
    return CostoItem(
        servicio='RDS',
        descripcion=f'{cantidad} instancia(s) {tipo_instancia} con {storage_gb}GB storage',
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
]
