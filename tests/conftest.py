import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / 'fixtures'


@pytest.fixture
def ec2_product() -> dict:
    return json.loads((FIXTURES / 'ec2_product.json').read_text(encoding='utf-8'))


@pytest.fixture(autouse=True)
def reset_pricing_cache():
    from backend.pricing_resolver import reset_cache_for_tests

    reset_cache_for_tests()
    yield
    reset_cache_for_tests()
