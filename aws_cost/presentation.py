"""Formato de estimaciones para CLI y GUI."""

from aws_cost.models import EstimadoCostoAWS


def estimacion_a_filas(estimacion: EstimadoCostoAWS) -> list[dict[str, object]]:
    """Convierte la estimación a filas para tablas (Streamlit, etc.)."""
    return [
        {
            'Servicio': item.servicio,
            'Descripcion': item.descripcion,
            'Cantidad': item.cantidad,
            'Costo mensual (USD)': round(item.costo_total_mensual, 2),
        }
        for item in estimacion.items
    ]


def formatear_estimacion_texto(estimacion: EstimadoCostoAWS) -> str:
    """Formato de texto plano para CLI o mensajes de chat."""
    lineas = [
        f'ESTIMACION AWS — Region: {estimacion.region}',
        '',
        f"{'Servicio':<25} {'Descripcion':<35} {'Qty':<5} {'Mensual':>12}",
        '-' * 80,
    ]
    for item in estimacion.items:
        lineas.append(
            f'{item.servicio:<25} {item.descripcion:<35} '
            f'{item.cantidad:<5} ${item.costo_total_mensual:>10.2f}'
        )
    lineas.extend([
        '-' * 80,
        f"{'TOTAL MENSUAL':<63} ${estimacion.total_mensual:.2f}",
        f"{'TOTAL ANUAL':<63} ${estimacion.total_anual:.2f}",
    ])
    if estimacion.notas:
        lineas.append('')
        lineas.append('NOTAS:')
        for nota in estimacion.notas:
            lineas.append(f'  - {nota}')
    return '\n'.join(lineas)
