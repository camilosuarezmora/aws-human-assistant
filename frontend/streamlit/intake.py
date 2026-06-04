"""Formulario inicial (intake) para usuarios no técnicos."""

import streamlit as st

from backend.models import ContextoNegocio, PreferenciaSimplicidad, RangoUsuarios, SensibilidadDatos
from backend.services.calculator import actualizar_contexto

TIPOS_NEGOCIO = [
    'Tienda online / e-commerce',
    'SaaS / aplicación web',
    'App móvil con backend',
    'Blog o sitio de contenidos',
    'Intranet / herramienta interna',
    'API o integración B2B',
    'Otro',
]

RANGOS_USUARIOS_LABELS = {
    'menos_50': 'Menos de 50 usuarios',
    '50_500': '50 – 500',
    '500_5000': '500 – 5.000',
    '5000_50000': '5.000 – 50.000',
    'mas_50000': 'Más de 50.000',
    'no_se': 'No lo sé / variable',
}

PREFERENCIAS = {
    'simple': 'Lo más simple posible (menos piezas que administrar)',
    'equilibrado': 'Equilibrado (coste y rendimiento razonables)',
    'rendimiento': 'Máximo rendimiento y escalabilidad',
}


def _mensaje_inicial_desde_contexto(ctx: ContextoNegocio) -> str:
    return (
        f'Tengo un proyecto de tipo "{ctx.tipo_negocio}". '
        f'{ctx.problema} '
        f'Usuarios esperados: {RANGOS_USUARIOS_LABELS[ctx.rango_usuarios]}. '
        f'Prefiero una solución {PREFERENCIAS[ctx.preferencia].lower()}.'
    )


def render_intake() -> bool:
    """
    Muestra el formulario de intake. Devuelve True si el usuario completó el intake
    y puede usar el chat.
    """
    if st.session_state.get('intake_completado') and st.session_state.get('contexto_negocio'):
        ctx: ContextoNegocio = st.session_state.contexto_negocio
        with st.expander('Tu perfil de negocio (editar)', expanded=False):
            st.markdown(f'**Negocio:** {ctx.tipo_negocio}')
            st.markdown(f'**Problema:** {ctx.problema}')
            st.markdown(f'**Usuarios:** {RANGOS_USUARIOS_LABELS[ctx.rango_usuarios]}')
            if ctx.presupuesto_mensual_usd:
                st.markdown(f'**Presupuesto:** ${ctx.presupuesto_mensual_usd:,.0f} USD/mes')
            st.markdown(f'**Región:** {ctx.region}')
            if st.button('Volver a rellenar el formulario'):
                st.session_state.intake_completado = False
                st.rerun()
        return True

    st.subheader('Cuéntanos tu proyecto')
    st.caption(
        'No necesitas conocer AWS. Responde en lenguaje cotidiano; '
        'después podrás afinar en el chat.'
    )

    with st.form('intake_form', clear_on_submit=False):
        tipo = st.selectbox('Tipo de negocio o proyecto', TIPOS_NEGOCIO)
        if tipo == 'Otro':
            tipo = st.text_input('Describe tu tipo de negocio')
        problema = st.text_area(
            '¿Qué quieres lograr? (una o dos frases)',
            placeholder='Ej.: Vender productos online con pagos y envíos',
            height=100,
        )
        rango_key = st.selectbox(
            '¿Cuántas personas usarán la solución?',
            options=list(RANGOS_USUARIOS_LABELS.keys()),
            format_func=lambda k: RANGOS_USUARIOS_LABELS[k],
        )
        sensibilidad = st.selectbox(
            'Sensibilidad de los datos',
            options=['baja', 'media', 'alta'],
            format_func=lambda x: {
                'baja': 'Baja (contenido público)',
                'media': 'Media (datos de clientes)',
                'alta': 'Alta (salud, finanzas, datos muy sensibles)',
            }[x],
        )
        col_a, col_b = st.columns(2)
        with col_a:
            presupuesto = st.number_input(
                'Presupuesto mensual aproximado (USD, opcional)',
                min_value=0.0,
                value=0.0,
                step=50.0,
                help='0 = sin límite definido',
            )
        with col_b:
            region = st.text_input(
                'Región AWS preferida',
                value='us-east-1',
                help='us-east-1 suele ser la más económica para empezar',
            )
        preferencia = st.radio(
            'Prioridad',
            options=list(PREFERENCIAS.keys()),
            format_func=lambda k: PREFERENCIAS[k],
            horizontal=False,
        )
        sin_servidores = st.checkbox('Prefiero no administrar servidores (serverless/contenedores gestionados)')
        enviado = st.form_submit_button('Continuar al asesor', type='primary', use_container_width=True)

    if not enviado:
        return False

    if not problema.strip():
        st.error('Describe qué quieres lograr con tu proyecto.')
        return False

    restricciones: list[str] = []
    if sin_servidores:
        restricciones.append('sin administrar servidores')

    ctx = ContextoNegocio(
        tipo_negocio=tipo or 'Otro',
        problema=problema.strip(),
        rango_usuarios=rango_key,
        sensibilidad_datos=sensibilidad,
        presupuesto_mensual_usd=presupuesto if presupuesto > 0 else None,
        region=region.strip() or 'us-east-1',
        preferencia=preferencia,
        restricciones=restricciones,
    )
    st.session_state.contexto_negocio = ctx
    st.session_state.intake_completado = True
    st.session_state.mensaje_inicial_pendiente = _mensaje_inicial_desde_contexto(ctx)

    if st.session_state.calculator_session is not None:
        actualizar_contexto(st.session_state.calculator_session, ctx)

    st.rerun()
    return False
