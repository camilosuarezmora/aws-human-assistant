"""Catálogo de servicios calculables para el agente arquitecto."""

from backend.models import ServicioCalculable

CAPACIDADES_CALCULO: dict[ServicioCalculable, str] = {
    'EC2': 'tipo_instancia, cantidad, region',
    'RDS': 'tipo_instancia, cantidad, storage_gb, region',
    'ElastiCache': 'tipo_instancia, cantidad',
    'S3': 'almacenamiento_gb',
    'Transferencia de Datos': 'gb_salientes',
    'Lambda': 'millones_peticiones, gb_segundos',
    'API Gateway': 'millones_peticiones',
    'DynamoDB': 'millones_escrituras, millones_lecturas',
    'SNS': 'millones_peticiones',
    'SQS': 'millones_peticiones',
    'ALB': 'cantidad (balanceadores)',
    'CloudFront': 'gb_salientes (tráfico CDN)',
    'Route53': 'hosted_zones',
    'Fargate': 'vcpu, memoria_gb, horas_mes',
    'ECS': 'cantidad, region (plano de control ECS)',
    'Cognito': 'usuarios_mau (usuarios activos mensuales)',
    'CloudWatch': 'gb_logs',
    'NAT Gateway': 'cantidad',
}


def listar_capacidades_calculo() -> str:
    """Texto para inyectar en prompts del arquitecto."""
    lineas = ['Servicios AWS con cálculo de costos disponible:']
    for servicio, params in CAPACIDADES_CALCULO.items():
        lineas.append(f'- {servicio}: {params}')
    return '\n'.join(lineas)
