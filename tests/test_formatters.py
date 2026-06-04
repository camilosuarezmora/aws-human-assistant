"""Tests de formateo y exportación."""

import json
from pathlib import Path

from backend.models import PropuestaCompletaAWS
from frontend.formatters import formatear_propuesta_markdown

FIXTURES = Path(__file__).parent / 'fixtures'


def test_formatear_propuesta_markdown():
    data = json.loads((FIXTURES / 'propuesta_estructura.json').read_text(encoding='utf-8'))
    prop = PropuestaCompletaAWS.model_validate(data)
    md = formatear_propuesta_markdown(prop)
    assert '# Propuesta AWS' in md
    assert 'Lambda' in md
    assert 'Hoja de ruta' in md
