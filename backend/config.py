from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GROQ_MODEL_NAME = 'llama-3.3-70b-versatile'
DEFAULT_REGION = 'us-east-1'


def load_environment() -> None:
    """Carga variables de entorno desde .env en la raíz del proyecto."""
    load_dotenv(PROJECT_ROOT / '.env')
