"""
Interfaz gráfica (Streamlit).

Ejecutar:
    streamlit run gui.py
"""

from backend.config import load_environment
from frontend.streamlit.app import run_app
from frontend.streamlit.env import streamlit_secrets_as_env

load_environment(extra_env=streamlit_secrets_as_env())

run_app()
