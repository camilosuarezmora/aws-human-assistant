"""Formato de estimaciones y propuestas para CLI y Streamlit."""

from backend.models import EstimadoCostoAWS, PropuestaCompletaAWS


def estimacion_a_filas(estimacion: EstimadoCostoAWS) -> list[dict[str, object]]:
    """Convierte la estimación a filas para tablas (Streamlit, etc.)."""
    return [
        {
            'Servicio': item.servicio,
            'Descripcion': item.descripcion,
            'Cantidad': item.cantidad,
            'Opcional': 'Sí' if item.es_opcional else 'No',
            'Costo mensual (USD)': round(item.costo_total_mensual, 2),
        }
        for item in estimacion.items
    ]


def formatear_estimacion_texto(estimacion: EstimadoCostoAWS) -> str:
    """Formato de texto plano para CLI o mensajes de chat."""
    lineas = [
        f'ESTIMACION AWS — Region: {estimacion.region}',
        '',
        f"{'Servicio':<22} {'Descripcion':<32} {'Qty':<5} {'Opc.':<5} {'Mensual':>12}",
        '-' * 82,
    ]
    for item in estimacion.items:
        opc = 'si' if item.es_opcional else 'no'
        lineas.append(
            f'{item.servicio:<22} {item.descripcion:<32} '
            f'{item.cantidad:<5} {opc:<5} ${item.costo_total_mensual:>10.2f}'
        )
    lineas.extend([
        '-' * 82,
        f"{'TOTAL MENSUAL':<65} ${estimacion.total_mensual:.2f}",
        f"{'TOTAL ANUAL':<65} ${estimacion.total_anual:.2f}",
    ])
    if estimacion.notas:
        lineas.append('')
        lineas.append('NOTAS:')
        for nota in estimacion.notas:
            lineas.append(f'  - {nota}')
    return '\n'.join(lineas)


def formatear_propuesta_markdown(propuesta: PropuestaCompletaAWS) -> str:
    """Exporta la propuesta completa en Markdown."""
    arch = propuesta.arquitectura
    est = propuesta.estimacion
    hoja = propuesta.hoja_ruta
    lineas = [
        '# Propuesta AWS',
        '',
        '## Resumen ejecutivo',
        arch.resumen_ejecutivo,
        '',
        '## Arquitectura',
    ]
    if arch.diagrama_mermaid.strip():
        lineas.extend(['```mermaid', arch.diagrama_mermaid.strip(), '```', ''])
    for comp in arch.componentes:
        opc = ' (opcional)' if comp.es_opcional else ''
        lineas.append(f'- **{comp.servicio}**{opc}: {comp.rol} — {comp.supuesto}')
    if arch.alternativas:
        lineas.extend(['', '### Alternativas', ''])
        for alt in arch.alternativas:
            lineas.append(f'- {alt}')
    if arch.riesgos:
        lineas.extend(['', '### Riesgos', ''])
        for r in arch.riesgos:
            lineas.append(f'- {r}')
    lineas.extend([
        '',
        '## Costes estimados',
        '',
        f'- **Total mensual:** ${est.total_mensual:,.2f} USD',
        f'- **Total anual:** ${est.total_anual:,.2f} USD',
        f'- **Región:** {est.region}',
    ])
    if propuesta.cumple_presupuesto is not None:
        estado = 'dentro del presupuesto' if propuesta.cumple_presupuesto else 'por encima del presupuesto'
        lineas.append(f'- **Presupuesto:** {estado}')
    lineas.append('')
    lineas.append('| Servicio | Descripción | Opcional | Mensual USD |')
    lineas.append('|----------|-------------|----------|-------------|')
    for item in est.items:
        lineas.append(
            f'| {item.servicio} | {item.descripcion} | '
            f'{"Sí" if item.es_opcional else "No"} | {item.costo_total_mensual:.2f} |'
        )
    if est.notas:
        lineas.extend(['', '### Notas de costes', ''])
        for nota in est.notas:
            lineas.append(f'- {nota}')
    if propuesta.opciones_reduccion_coste:
        lineas.extend(['', '## Opciones para reducir coste', ''])
        for o in propuesta.opciones_reduccion_coste:
            lineas.append(f'- {o}')
    lineas.extend(['', '## Hoja de ruta', '', hoja.resumen, ''])
    for i, fase in enumerate(hoja.fases, 1):
        lineas.append(f'### {i}. {fase.titulo} (esfuerzo: {fase.esfuerzo})')
        lineas.append(fase.descripcion)
        for paso in fase.pasos:
            lineas.append(f'- {paso}')
        for enlace in fase.enlaces:
            lineas.append(f'- Doc: {enlace}')
    if hoja.checklist_alto_nivel:
        lineas.extend(['', '### Checklist', ''])
        for item in hoja.checklist_alto_nivel:
            lineas.append(f'- [ ] {item}')
    if hoja.anexo_tecnico_iam_vpc.strip():
        lineas.extend(['', '## Anexo técnico (IAM / VPC)', '', hoja.anexo_tecnico_iam_vpc])
    lineas.extend(['', '---', propuesta.advertencia_legal])
    return '\n'.join(lineas)
