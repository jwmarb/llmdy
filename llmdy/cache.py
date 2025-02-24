from llmdy.constants import CACHE_STRATEGY, CACHE_TTL
from llmdy.util import client
from cachetools import TTLCache


def __generate_key__(key: str) -> str:
    return f"cache:{key}"


class Cache:
    __memory__ = TTLCache(ttl=CACHE_TTL, maxsize=10)

    @staticmethod
    def insert(key: str, value: str):
        """
        Inserts a key-value pair into the cache

        :param key: The key to insert
        :param value: The associated value
        """

        key = __generate_key__(key)
        match CACHE_STRATEGY:
            case 'memory':
                Cache.__memory__[key] = value
            case 'redis':
                client.setex(key, CACHE_TTL, value)
            case 'none':
                pass

    @staticmethod
    def get(key: str):
        """
        Gets the key from cache, if it exists. Otherwise, returns None

        :param key: The key to retrieve
        :return: The associated value or None if the key does not exist in the cache
        """
        key = __generate_key__(key)
        match CACHE_STRATEGY:
            case 'memory':
                return Cache.__memory__.get(key)
            case 'redis':
                return client.get(key)
            case 'none':
                return None
