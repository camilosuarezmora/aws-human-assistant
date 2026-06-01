"""
Calculador de Costos de AWS con Pydantic AI.

  CLI:  python main.py
  GUI:  python main.py --gui
        streamlit run gui.py
"""

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

from backend.config import load_environment

load_environment()


def _launch_gui() -> None:
    gui_path = Path(__file__).resolve().parent / 'gui.py'
    subprocess.run(
        [sys.executable, '-m', 'streamlit', 'run', str(gui_path), '--server.headless', 'true'],
        check=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description='Calculadora de costos AWS')
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Abre la interfaz grafica (Streamlit)',
    )
    args = parser.parse_args()

    if args.gui:
        _launch_gui()
    else:
        from frontend.cli.app import run as run_cli

        asyncio.run(run_cli())


if __name__ == '__main__':
    main()
