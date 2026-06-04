"""Componentes reutilizables de la interfaz Streamlit."""

import streamlit as st

from backend.models import EstimadoCostoAWS, PropuestaCompletaAWS
from backend.services.calculator import reiniciar_sesion
from frontend.formatters import (
    estimacion_a_filas,
    formatear_estimacion_texto,
    formatear_propuesta_markdown,
)

GLOSARIO = {
    'EC2': 'Servidores virtuales en la nube (como un ordenador remoto).',
    'RDS': 'Base de datos gestionada (MySQL, PostgreSQL, etc.).',
    'Lambda': 'Ejecuta código solo cuando ocurre un evento; pagas por uso.',
    'S3': 'Almacenamiento de archivos (imágenes, copias de seguridad, etc.).',
    'Fargate': 'Contenedores sin gestionar servidores físicos.',
    'CloudFront': 'Red de entrega de contenidos (acelera tu web en todo el mundo).',
    'VPC': 'Red privada virtual: aísla tus recursos en AWS.',
    'IAM': 'Gestión de quién puede hacer qué en tu cuenta AWS.',
}


def render_glossary() -> None:
    with st.expander('Glosario (en una frase)'):
        for term, desc in GLOSARIO.items():
            st.markdown(f'**{term}:** {desc}')


def render_sidebar() -> None:
    """Barra lateral con información y acciones."""
    with st.sidebar:
        st.title('Asesor AWS')
        st.markdown(
            """
            Traduce tu problema de negocio en una solución en AWS
            con costes estimados y una hoja de ruta paso a paso.
            """
        )
        render_glossary()
        st.divider()
        st.markdown('**Ejemplos en el chat**')
        st.caption('Quiero una app de reservas para 20 empleados')
        st.caption('Tienda online con 500 visitas al día')
        st.caption('Reduce el coste quitando lo opcional')
        if st.button('Nueva conversacion', use_container_width=True):
            st.session_state.ui_messages = []
            st.session_state.intake_completado = False
            st.session_state.pop('contexto_negocio', None)
            st.session_state.pop('mensaje_inicial_pendiente', None)
            if st.session_state.calculator_session is not None:
                reiniciar_sesion(st.session_state.calculator_session)
            st.rerun()


def render_estimacion(estimacion: EstimadoCostoAWS) -> str:
    """Muestra tabla, métricas y notas."""
    col1, col2, col3 = st.columns(3)
    col1.metric('Total mensual (USD)', f'{estimacion.total_mensual:,.2f}')
    col2.metric('Total anual (USD)', f'{estimacion.total_anual:,.2f}')
    col3.metric('Region', estimacion.region)

    st.dataframe(estimacion_a_filas(estimacion), use_container_width=True, hide_index=True)

    if estimacion.notas:
        st.warning('Notas')
        for nota in estimacion.notas:
            st.markdown(f'- {nota}')

    return formatear_estimacion_texto(estimacion)


def render_propuesta(propuesta: PropuestaCompletaAWS, *, widget_key: str) -> str:
    """Vista con pestañas: resumen, costes, hoja de ruta, exportar."""
    arch = propuesta.arquitectura
    est = propuesta.estimacion

    if propuesta.cumple_presupuesto is False:
        st.error('La estimación supera tu presupuesto mensual indicado.')
        for tip in propuesta.opciones_reduccion_coste:
            st.info(tip)
    elif propuesta.cumple_presupuesto is True:
        st.success('La estimación está dentro de tu presupuesto mensual.')

    tab_resumen, tab_costes, tab_ruta, tab_export = st.tabs(
        ['Resumen', 'Costes', 'Hoja de ruta', 'Exportar'],
        key=f'{widget_key}_tabs',
    )

    with tab_resumen:
        st.markdown(arch.resumen_ejecutivo)
        if arch.diagrama_mermaid.strip():
            st.markdown('#### Diagrama')
            st.markdown(f'```mermaid\n{arch.diagrama_mermaid.strip()}\n```')
        if arch.componentes:
            st.markdown('#### Componentes')
            for c in arch.componentes:
                badge = ' *(opcional)*' if c.es_opcional else ''
                st.markdown(f'- **{c.servicio}**{badge}: {c.rol} — _{c.supuesto}_')
        if arch.alternativas:
            st.markdown('#### Alternativas')
            for a in arch.alternativas:
                st.markdown(f'- {a}')
        if arch.riesgos:
            st.markdown('#### Riesgos')
            for r in arch.riesgos:
                st.markdown(f'- {r}')
        if arch.preguntas_abiertas:
            st.markdown('#### Para afinar')
            for p in arch.preguntas_abiertas:
                st.markdown(f'- {p}')

    with tab_costes:
        render_estimacion(est)

    with tab_ruta:
        st.markdown(propuesta.hoja_ruta.resumen)
        for i, fase in enumerate(propuesta.hoja_ruta.fases, 1):
            with st.expander(
                f'{i}. {fase.titulo} — esfuerzo {fase.esfuerzo}',
                key=f'{widget_key}_fase_{i}',
            ):
                st.markdown(fase.descripcion)
                for paso in fase.pasos:
                    st.markdown(f'- {paso}')
                for enlace in fase.enlaces:
                    st.markdown(f'- [{enlace}]({enlace})')
        if propuesta.hoja_ruta.checklist_alto_nivel:
            st.markdown('#### Checklist')
            for item in propuesta.hoja_ruta.checklist_alto_nivel:
                st.markdown(f'- [ ] {item}')
        if propuesta.hoja_ruta.anexo_tecnico_iam_vpc.strip():
            with st.expander('Anexo técnico: IAM y VPC', key=f'{widget_key}_anexo'):
                st.markdown(propuesta.hoja_ruta.anexo_tecnico_iam_vpc)

    with tab_export:
        md = formatear_propuesta_markdown(propuesta)
        st.download_button(
            'Descargar propuesta (.md)',
            data=md,
            file_name='propuesta_aws.md',
            mime='text/markdown',
            use_container_width=True,
            key=f'{widget_key}_download',
        )
        st.caption(propuesta.advertencia_legal)

    return formatear_propuesta_markdown(propuesta)


def render_chat_history() -> None:
    """Pinta los mensajes guardados en session_state."""
    for idx, msg in enumerate(st.session_state.ui_messages):
        with st.chat_message(msg['role']):
            if msg.get('propuesta'):
                render_propuesta(msg['propuesta'], widget_key=f'propuesta_msg_{idx}')
            elif msg.get('estimacion'):
                render_estimacion(msg['estimacion'])
            else:
                st.markdown(msg['content'])
