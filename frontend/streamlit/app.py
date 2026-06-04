"""Aplicación Streamlit — asesor AWS para usuarios no técnicos."""

import asyncio

import streamlit as st

from backend.config import groq_api_key_configured, load_environment
from backend.models import ContextoNegocio
from backend.services.calculator import crear_sesion, procesar_mensaje, actualizar_contexto
from frontend.streamlit.components import render_chat_history, render_sidebar
from frontend.streamlit.env import streamlit_secrets_as_env
from frontend.streamlit.intake import render_intake

FASES_SPINNER = {
    None: 'Procesando tu consulta...',
    'costes': 'Calculando costes...',
    'completo': 'Diseñando solución, calculando costes y preparando hoja de ruta...',
}


def _ensure_groq_configured() -> bool:
    load_environment(extra_env=streamlit_secrets_as_env())
    return groq_api_key_configured()


def _ensure_calculator_session() -> bool:
    if st.session_state.get('calculator_session') is not None:
        return True
    if not _ensure_groq_configured():
        return False
    ctx = st.session_state.get('contexto_negocio')
    st.session_state.calculator_session = crear_sesion(
        ctx if isinstance(ctx, ContextoNegocio) else None,
    )
    return True


def _render_missing_api_key_help() -> None:
    st.error('Falta la API key de Groq (GROQ_API_KEY).')
    st.markdown(
        """
        **En Streamlit Cloud**

        1. Abre tu app en [share.streamlit.io](https://share.streamlit.io).
        2. Menú **⋮** → **Settings** → **Secrets**.
        3. Añade (sustituye por tu clave real):

        ```toml
        GROQ_API_KEY = "gsk_..."
        ```

        4. Guarda y espera a que la app se reinicie.

        **En local**

        Crea `.streamlit/secrets.toml` a partir de `.streamlit/secrets.toml.example`
        o define `GROQ_API_KEY` en `.env` en la raíz del proyecto.

        Obtén una clave en [Groq Console](https://console.groq.com/).
        """
    )


def _init_session_state() -> None:
    if 'ui_messages' not in st.session_state:
        st.session_state.ui_messages = []
    if 'calculator_session' not in st.session_state:
        st.session_state.calculator_session = None
    if 'intake_completado' not in st.session_state:
        st.session_state.intake_completado = False


def _append_message(role: str, content: str, *, estimacion=None, propuesta=None) -> None:
    entry: dict = {'role': role, 'content': content}
    if estimacion is not None:
        entry['estimacion'] = estimacion
    if propuesta is not None:
        entry['propuesta'] = propuesta
    st.session_state.ui_messages.append(entry)


async def _handle_prompt(prompt: str) -> None:
    if not _ensure_calculator_session():
        _append_message(
            'assistant',
            '**Error:** Configura GROQ_API_KEY en los Secrets de Streamlit Cloud o en .env.',
        )
        return
    sesion = st.session_state.calculator_session
    if st.session_state.get('contexto_negocio'):
        actualizar_contexto(sesion, st.session_state.contexto_negocio)
    result = await procesar_mensaje(sesion, prompt)

    if result.advertencia:
        _append_message('assistant', f'**Aviso:** {result.advertencia}')
        return

    if result.error:
        _append_message('assistant', f'**Error:** {result.error}')
        return

    if result.propuesta:
        _append_message('assistant', '', propuesta=result.propuesta)
    elif result.estimacion:
        _append_message('assistant', '', estimacion=result.estimacion)


def run_app() -> None:
    """Punto de entrada de la GUI Streamlit."""
    st.set_page_config(
        page_title='Asesor AWS',
        page_icon='☁️',
        layout='wide',
        initial_sidebar_state='expanded',
    )
    _init_session_state()
    render_sidebar()

    st.title('Asesor AWS')
    st.caption('De tu problema de negocio a una solución en la nube con costes estimados')

    if not _ensure_groq_configured():
        _render_missing_api_key_help()
        return

    if not _ensure_calculator_session():
        st.warning('No se pudo iniciar el asesor. Revisa la configuración de GROQ_API_KEY.')
        return

    if not render_intake():
        return

    render_chat_history()

    pendiente = st.session_state.pop('mensaje_inicial_pendiente', None)
    if pendiente and not any(m['role'] == 'user' for m in st.session_state.ui_messages):
        _append_message('user', pendiente)
        with st.spinner(FASES_SPINNER['completo']):
            asyncio.run(_handle_prompt(pendiente))
        st.rerun()

    if prompt := st.chat_input(
        'Describe tu necesidad o pide cambios (ej. menos presupuesto, añadir base de datos)...',
    ):
        _append_message('user', prompt)
        with st.spinner(FASES_SPINNER['completo']):
            asyncio.run(_handle_prompt(prompt))
        st.rerun()
