import time

from backend.pricing_cache import PricingCache, make_cache_key


def test_cache_hit_and_miss():
    cache = PricingCache(ttl_seconds=60)
    key = make_cache_key('AmazonEC2', 'us-east-1', 't3.micro')
    assert cache.get(key) is None
    cache.set(key, 0.01)
    assert cache.get(key) == 0.01


def test_cache_expira():
    cache = PricingCache(ttl_seconds=0.05)
    key = 'k'
    cache.set(key, 1.0)
    time.sleep(0.06)
    assert cache.get(key) is None


def test_cache_clear():
    cache = PricingCache(ttl_seconds=60)
    cache.set('a', 1)
    cache.clear()
    assert cache.get('a') is None
