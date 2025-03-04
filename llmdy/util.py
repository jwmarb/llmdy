from llmdy.constants import REDIS_URI
import redis

client = redis.Redis.from_url(REDIS_URI) if REDIS_URI else None
