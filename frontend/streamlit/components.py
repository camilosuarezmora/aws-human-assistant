"""Componentes reutilizables de la interfaz Streamlit."""

import streamlit as st

from backend.models import EstimadoCostoAWS
from backend.services.calculator import reiniciar_sesion
from frontend.formatters import estimacion_a_filas, formatear_estimacion_texto


def render_sidebar() -> None:
    """Barra lateral con información y acciones."""
    with st.sidebar:
        st.title('AWS Cost Calculator')
        st.markdown(
            """
            Estima costos mensuales y anuales de infraestructura AWS
            a partir de descripciones en lenguaje natural.

            **Servicios soportados:** EC2, RDS, S3, Lambda, API Gateway,
            DynamoDB, ElastiCache, SNS, SQS y transferencia de datos.
            """
        )
        st.divider()
        st.markdown('**Ejemplos**')
        st.caption('3 instancias t3.medium en us-east-1')
        st.caption('1 RDS db.t3.small con 100 GB')
        st.caption('Lambda + API Gateway + DynamoDB para 1M req/mes')
        if st.button('Nueva conversacion', use_container_width=True):
            st.session_state.ui_messages = []
            if st.session_state.calculator_session is not None:
                reiniciar_sesion(st.session_state.calculator_session)
            st.rerun()


def render_estimacion(estimacion: EstimadoCostoAWS) -> str:
    """Muestra tabla, métricas y notas. Devuelve texto para el historial de chat."""
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


def render_chat_history() -> None:
    """Pinta los mensajes guardados en session_state."""
    for msg in st.session_state.ui_messages:
        with st.chat_message(msg['role']):
            if msg.get('estimacion'):
                render_estimacion(msg['estimacion'])
            else:
                st.markdown(msg['content'])
