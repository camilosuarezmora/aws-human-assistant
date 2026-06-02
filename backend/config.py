import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GROQ_MODEL_NAME = 'llama-3.3-70b-versatile'
DEFAULT_REGION = 'us-east-1'


def load_environment() -> None:
    """Carga variables de entorno desde .env en la raíz del proyecto."""
    load_dotenv(PROJECT_ROOT / '.env')


def _env_bool(name: str, default: str = 'true') -> bool:
    return os.getenv(name, default).lower() in ('1', 'true', 'yes')


def pricing_api_region() -> str:
    """Región del endpoint del cliente pricing (no la región del recurso)."""
    return os.getenv('PRICING_API_REGION', 'us-east-1')


def pricing_cache_ttl_seconds() -> int:
    return int(os.getenv('PRICING_CACHE_TTL_SECONDS', str(24 * 3600)))


def aws_pricing_enabled() -> bool:
    return _env_bool('AWS_PRICING_ENABLED', 'true')
