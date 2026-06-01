"""
Interfaz gráfica (Streamlit).

Ejecutar:
    streamlit run gui.py
"""

from aws_cost.config import load_environment
from aws_cost.ui.streamlit_app import run_app

load_environment()

run_app()
