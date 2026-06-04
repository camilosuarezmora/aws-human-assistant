"""Compatibilidad: la carga de secretos vive en backend.config."""

from backend.config import streamlit_secrets_as_env

__all__ = ['streamlit_secrets_as_env']
