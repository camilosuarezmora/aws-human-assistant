from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_environment() -> None:
    """Carga variables de entorno desde .env en la raíz del proyecto."""
    load_dotenv(_PROJECT_ROOT / '.env')
