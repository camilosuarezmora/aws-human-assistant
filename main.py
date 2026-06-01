"""
Calculador de Costos de AWS con Pydantic AI.

Punto de entrada: python main.py
"""

import asyncio

from aws_cost.config import load_environment
from aws_cost.cli import main as run_cli

load_environment()

if __name__ == '__main__':
    asyncio.run(run_cli())
