import llmdy
import fakeredis


def test_cache_memory():
    llmdy.cache.CACHE_STRATEGY = "memory"

    Cache = llmdy.cache.Cache

    assert Cache.get("hello") == None
    Cache.insert("hello", "world")
    assert Cache.get("hello") == "world"


def test_cache_redis():
    llmdy.cache.CACHE_STRATEGY = "redis"
    llmdy.cache.rediscli = fakeredis.FakeRedis()
    Cache = llmdy.cache.Cache

    assert Cache.get("hello") == None
    Cache.insert("hello", "world")
    assert Cache.get("hello") == "world"

    assert len(llmdy.cache.rediscli.keys()) > 0


def test_cache_none():
    llmdy.cache.CACHE_STRATEGY = "none"
    Cache = llmdy.cache.Cache
    llmdy.cache.rediscli = fakeredis.FakeRedis()

    assert Cache.get("hello") == None
    Cache.insert("hello", "world")
    assert Cache.get("hello") == None
    assert Cache.__memory__.get("hello") == None
    assert len(llmdy.cache.rediscli.keys()) == 0
