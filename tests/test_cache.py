import time
import pytest
from server.cache import Cache

def test_cache_set_get():
    c = Cache(ttl=5)
    c.set("BTC", 123)
    assert c.get("BTC") == 123

def test_cache_ttl_expires():
    c = Cache(ttl=1)
    c.set("TEST", "value")
    assert c.get("TEST") == "value"
    time.sleep(1.1)
    assert c.get("TEST") is None
