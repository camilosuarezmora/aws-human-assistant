from typing import List, Literal, Optional

from pydantic import BaseModel, Field

# Servicios con herramienta de cálculo de costos disponible
ServicioCalculable = Literal[
    'EC2',
    'RDS',
    'ElastiCache',
    'S3',
    'Transferencia de Datos',
    'Lambda',
    'API Gateway',
    'DynamoDB',
    'SNS',
    'SQS',
    'ALB',
    'CloudFront',
    'Route53',
    'Fargate',
    'ECS',
    'Cognito',
    'CloudWatch',
    'NAT Gateway',
]

CategoriaValidacion = Literal[
    'problema_negocio',
    'refinamiento',
    'aws_costos',
    'off_topic',
    'ambiguo',
]

PreferenciaSimplicidad = Literal['simple', 'equilibrado', 'rendimiento']

RangoUsuarios = Literal[
    'menos_50',
    '50_500',
    '500_5000',
    '5000_50000',
    'mas_50000',
    'no_se',
]

SensibilidadDatos = Literal['baja', 'media', 'alta']


class CostoItem(BaseModel):
    """Un ítem de costo individual."""

    servicio: str = Field(..., description='Nombre del servicio AWS')
    descripcion: str = Field(..., description='Descripción del recurso')
    cantidad: int = Field(..., description='Cantidad de recursos')
    costo_unitario_mensual: float = Field(..., description='Costo unitario por mes en USD')
    costo_total_mensual: float = Field(..., description='Costo total mensual en USD')
    es_opcional: bool = Field(
        default=False,
        description='True si el recurso es opcional en la arquitectura',
    )


class EstimadoCostoAWS(BaseModel):
    """Estimación completa de costos AWS."""

    items: List[CostoItem] = Field(..., description='Lista de todos los recursos con costos')
    total_mensual: float = Field(..., description='Total mensual en USD')
    total_anual: float = Field(..., description='Total anual en USD')
    region: str = Field(
        default='us-east-1',
        description='Región de AWS usada para los precios',
    )
    notas: List[str] = Field(
        default_factory=list,
        description='Notas y advertencias sobre los costos',
    )


class ValidacionPrompt(BaseModel):
    """Resultado de clasificar si un mensaje pertenece al asesor AWS."""

    es_relevante: bool = Field(
        description='True si el mensaje describe un problema de negocio o costos AWS',
    )
    categoria: CategoriaValidacion = Field(description='Tipo de intención detectada')
    mensaje: str = Field(
        description='Mensaje breve para el usuario si no es relevante o es ambiguo',
    )


class ContextoNegocio(BaseModel):
    """Datos del formulario inicial (intake) y preferencias del usuario."""

    tipo_negocio: str = Field(..., description='Ej. tienda online, SaaS, blog')
    problema: str = Field(..., description='Descripción del problema en una frase')
    rango_usuarios: RangoUsuarios = Field(default='no_se')
    sensibilidad_datos: SensibilidadDatos = Field(default='media')
    presupuesto_mensual_usd: Optional[float] = Field(
        default=None,
        description='Presupuesto mensual objetivo en USD, si lo indicó',
    )
    region: str = Field(default='us-east-1')
    preferencia: PreferenciaSimplicidad = Field(default='equilibrado')
    restricciones: List[str] = Field(
        default_factory=list,
        description='Ej. sin administrar servidores',
    )


class ComponenteAWS(BaseModel):
    """Recurso AWS propuesto con parámetros para las tools de costos."""

    servicio: ServicioCalculable
    rol: str = Field(..., description='Rol en la solución en lenguaje llano')
    supuesto: str = Field(..., description='Supuesto de tamaño en lenguaje humano')
    es_opcional: bool = False
    tipo_instancia: Optional[str] = None
    cantidad: int = 1
    storage_gb: Optional[int] = None
    almacenamiento_gb: Optional[float] = None
    gb_salientes: Optional[float] = None
    millones_peticiones: Optional[float] = None
    gb_segundos: Optional[float] = None
    millones_escrituras: Optional[float] = None
    millones_lecturas: Optional[float] = None
    vcpu: Optional[float] = None
    memoria_gb: Optional[float] = None
    horas_mes: Optional[float] = None
    hosted_zones: Optional[int] = None
    usuarios_mau: Optional[int] = None
    gb_logs: Optional[float] = None
    region: str = 'us-east-1'


class PropuestaArquitectura(BaseModel):
    """Arquitectura AWS traducida desde el problema de negocio."""

    resumen_ejecutivo: str = Field(..., description='2-3 párrafos en español claro')
    componentes: List[ComponenteAWS]
    alternativas: List[str] = Field(default_factory=list)
    riesgos: List[str] = Field(default_factory=list)
    preguntas_abiertas: List[str] = Field(default_factory=list)
    diagrama_mermaid: str = Field(
        default='',
        description='Diagrama Mermaid simple de la arquitectura',
    )


class FaseHojaRuta(BaseModel):
    """Una fase de la hoja de ruta de implementación."""

    titulo: str
    descripcion: str
    pasos: List[str] = Field(default_factory=list)
    esfuerzo: Literal['bajo', 'medio', 'alto'] = 'medio'
    enlaces: List[str] = Field(default_factory=list)


class HojaRutaAWS(BaseModel):
    """Guía de implementación en AWS (incluye IAM/VPC)."""

    resumen: str
    fases: List[FaseHojaRuta]
    checklist_alto_nivel: List[str] = Field(default_factory=list)
    anexo_tecnico_iam_vpc: str = Field(
        default='',
        description='Detalle IAM, VPC y red para perfiles semi-técnicos',
    )


class PropuestaCompletaAWS(BaseModel):
    """Entregable final del asesor."""

    arquitectura: PropuestaArquitectura
    estimacion: EstimadoCostoAWS
    hoja_ruta: HojaRutaAWS
    cumple_presupuesto: Optional[bool] = None
    opciones_reduccion_coste: List[str] = Field(default_factory=list)
    advertencia_legal: str = Field(
        default=(
            'Estimación orientativa basada en precios públicos de AWS; '
            'no sustituye la factura real ni la Calculadora oficial de AWS.'
        ),
    )
