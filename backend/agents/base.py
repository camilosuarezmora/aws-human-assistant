from pydantic_ai.models.groq import GroqModel

from backend.config import GROQ_MODEL_NAME


def crear_modelo_groq() -> GroqModel:
    """Factory del modelo Groq usado por todos los agentes."""
    return GroqModel(model_name=GROQ_MODEL_NAME)
