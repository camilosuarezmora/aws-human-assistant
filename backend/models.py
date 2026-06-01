from typing import List, Literal

from pydantic import BaseModel, Field


class CostoItem(BaseModel):
    """Un ítem de costo individual."""

    servicio: str = Field(..., description='Nombre del servicio AWS')
    descripcion: str = Field(..., description='Descripción del recurso')
    cantidad: int = Field(..., description='Cantidad de recursos')
    costo_unitario_mensual: float = Field(..., description='Costo unitario por mes en USD')
    costo_total_mensual: float = Field(..., description='Costo total mensual en USD')


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
    """Resultado de clasificar si un mensaje pertenece a esta calculadora."""

    es_relevante: bool = Field(
        description='True si el mensaje pide estimar costos de infraestructura AWS',
    )
    categoria: Literal['aws_costos', 'off_topic', 'ambiguo'] = Field(
        description='Tipo de intención detectada',
    )
    mensaje: str = Field(
        description='Mensaje breve para el usuario si no es relevante o es ambiguo',
    )
