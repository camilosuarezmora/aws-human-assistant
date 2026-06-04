"""Carga de secretos de Streamlit Cloud en variables de entorno."""

from __future__ import annotations

from backend.config import STREAMLIT_SECRET_KEYS


def streamlit_secrets_as_env() -> dict[str, str]:
    """Lee st.secrets y devuelve pares para load_environment(extra_env=...)."""
    try:
        import streamlit as st
    except ImportError:
        return {}

    values: dict[str, str] = {}
    for key in STREAMLIT_SECRET_KEYS:
        if key not in st.secrets:
            continue
        raw = st.secrets[key]
        if raw is None:
            continue
        text = str(raw).strip()
        if text:
            values[key] = text
    return values
