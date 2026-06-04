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
)


def _apply_env_vars(values: dict[str, str] | None) -> None:
    if not values:
        return
    for key, value in values.items():
        if value and key not in os.environ:
            os.environ[key] = value


def streamlit_secrets_as_env() -> dict[str, str]:
    """
    Lee st.secrets (Streamlit Cloud o secrets.toml local) para load_environment.
    Devuelve {} si Streamlit no está disponible o no hay secretos configurados.
    """
    try:
        import streamlit as st
    except ImportError:
        return {}

    values: dict[str, str] = {}
    try:
        for key in STREAMLIT_SECRET_KEYS:
            if key not in st.secrets:
                continue
            raw = st.secrets[key]
            if raw is None:
                continue
            text = str(raw).strip()
            if text:
                values[key] = text
    except Exception:
        # Sin secrets.toml (desarrollo con solo .env) o fuera del runtime de Streamlit.
        return {}
    return values


def _streamlit_runtime_active() -> bool:
    """True si el script se ejecuta dentro de `streamlit run` (no en CLI pura)."""
    try:
        from streamlit.runtime.scriptrunner_utils.script_run_context import (
            get_script_run_ctx,
        )

        return get_script_run_ctx() is not None
    except Exception:
        return False


def load_environment(*, extra_env: dict[str, str] | None = None) -> None:
    """
    Carga variables de entorno para dev y producción con el mismo código.

    1. `.env` en la raíz del proyecto (desarrollo local).
    2. Si corre bajo Streamlit, añade claves de `st.secrets` que aún no estén definidas
       (Streamlit Cloud o `.streamlit/secrets.toml`).
    3. `extra_env` opcional para inyectar pares adicionales en tests u otros hosts.
    """
    load_dotenv(PROJECT_ROOT / '.env')
    merged: dict[str, str] = {}
    if _streamlit_runtime_active():
        merged.update(streamlit_secrets_as_env())
    if extra_env:
        merged.update(extra_env)
    _apply_env_vars(merged)


def groq_api_key_configured() -> bool:
    return bool(os.getenv('GROQ_API_KEY', '').strip())


def pricing_api_region() -> str:
    """Región del endpoint del cliente pricing (no la región del recurso)."""
    return os.getenv('PRICING_API_REGION', 'us-east-1')


def pricing_cache_ttl_seconds() -> int:
    return int(os.getenv('PRICING_CACHE_TTL_SECONDS', str(24 * 3600)))
