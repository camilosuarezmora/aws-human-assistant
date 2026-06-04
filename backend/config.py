import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GROQ_MODEL_NAME = 'llama-3.3-70b-versatile'
DEFAULT_REGION = 'us-east-1'

# Variables que Streamlit Cloud suele definir en Secrets (además de .env local).
STREAMLIT_SECRET_KEYS = (
    'GROQ_API_KEY',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_DEFAULT_REGION',
    'PRICING_API_REGION',
    'PRICING_CACHE_TTL_SECONDS',
    'AWS_PRICING_ENABLED',
)


def _apply_env_vars(values: dict[str, str] | None) -> None:
    if not values:
        return
    for key, value in values.items():
        if value and key not in os.environ:
            os.environ[key] = value


def load_environment(*, extra_env: dict[str, str] | None = None) -> None:
    """Carga .env y, opcionalmente, variables extra (p. ej. st.secrets en Streamlit Cloud)."""
    load_dotenv(PROJECT_ROOT / '.env')
    _apply_env_vars(extra_env)


def groq_api_key_configured() -> bool:
    return bool(os.getenv('GROQ_API_KEY', '').strip())


def _env_bool(name: str, default: str = 'true') -> bool:
    return os.getenv(name, default).lower() in ('1', 'true', 'yes')


def pricing_api_region() -> str:
    """Región del endpoint del cliente pricing (no la región del recurso)."""
    return os.getenv('PRICING_API_REGION', 'us-east-1')


def pricing_cache_ttl_seconds() -> int:
    return int(os.getenv('PRICING_CACHE_TTL_SECONDS', str(24 * 3600)))


def aws_pricing_enabled() -> bool:
    return _env_bool('AWS_PRICING_ENABLED', 'true')
