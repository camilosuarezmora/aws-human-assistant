"""Aplicación Streamlit — interfaz gráfica principal."""

import asyncio

import streamlit as st

from backend.services.calculator import crear_sesion, procesar_mensaje
from frontend.formatters import formatear_estimacion_texto
from frontend.streamlit.components import render_chat_history, render_sidebar


def _init_session_state() -> None:
    if 'ui_messages' not in st.session_state:
        st.session_state.ui_messages = []
    if 'calculator_session' not in st.session_state:
        st.session_state.calculator_session = crear_sesion()


def _append_message(role: str, content: str, *, estimacion=None) -> None:
    entry: dict = {'role': role, 'content': content}
    if estimacion is not None:
        entry['estimacion'] = estimacion
    st.session_state.ui_messages.append(entry)


async def _handle_prompt(prompt: str) -> None:
    sesion = st.session_state.calculator_session
    result = await procesar_mensaje(sesion, prompt)

    if result.advertencia:
        _append_message('assistant', f'**Advertencia:** {result.advertencia}')
        return

    if result.error:
        _append_message('assistant', f'**Error:** {result.error}')
        return

    if result.estimacion:
        texto = formatear_estimacion_texto(result.estimacion)
        _append_message('assistant', texto, estimacion=result.estimacion)


def run_app() -> None:
    """Punto de entrada de la GUI Streamlit."""
    st.set_page_config(
        page_title='Calculadora de costos AWS',
        page_icon='💰',
        layout='wide',
        initial_sidebar_state='expanded',
    )
    _init_session_state()
    render_sidebar()

    st.title('Calculadora de costos AWS')
    st.caption('Powered by Pydantic AI + Groq')

    render_chat_history()

    if prompt := st.chat_input('Describe tu infraestructura AWS...'):
        _append_message('user', prompt)
        with st.spinner('Validando y calculando costos...'):
            asyncio.run(_handle_prompt(prompt))
        st.rerun()
