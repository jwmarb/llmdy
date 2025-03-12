from llmdy.constants import AGENT_API_KEY, AGENT_BASE_URL, OPENAI_API_KEY, OPENAI_BASE_URL, REDIS_URI, WHISPER_API_KEY, WHISPER_BASE_URL
import openai
import redis

rediscli = redis.Redis.from_url(REDIS_URI) if REDIS_URI else None

agent = openai.Client(api_key=AGENT_API_KEY, base_url=AGENT_BASE_URL)

readerlm = openai.Client(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

whisper = openai.Client(api_key=WHISPER_API_KEY, base_url=WHISPER_BASE_URL)
