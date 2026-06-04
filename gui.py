"""
Interfaz gráfica (Streamlit).

Ejecutar:
    streamlit run gui.py
"""

from backend.config import load_environment
from frontend.streamlit.app import run_app

load_environment()

run_app()
