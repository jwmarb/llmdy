import os
from typing import Literal
import dotenv
import redis

dotenv.load_dotenv(dotenv_path=os.getenv("ENV_PATH", ".env"), override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY must be set in the environment variables")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

if OPENAI_BASE_URL is None:
    raise ValueError(
        "OPENAI_BASE_URL must be set in the environment variables")

READERLM_MODEL = os.getenv("READERLM_MODEL")

if READERLM_MODEL is None:
    raise ValueError("READERLM_MODEL must be set in the environment variables")

CACHE_STRATEGY: Literal['memory', 'redis',
                        'none'] = os.getenv("CACHE_STRATEGY", 'memory')

RECOVERY_STRATEGY: Literal['redis', 'disk',
                           'none'] = os.getenv('RECOVERY_STRATEGY', 'disk')

CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

if CACHE_TTL < 0:
    raise ValueError("CACHE_TTL must be a non-negative integer")

REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379/0")

if REDIS_URI != None:
    response = redis.Redis.from_url(REDIS_URI).ping()
    if response == False:
        raise ValueError(
            f"Failed to connect to redis instance. Is it running?\n\tURL: \"{REDIS_URI}\"")


READERLM_PROMPT = """<|im_start|>Extract the main content from the given HTML and convert it to Markdown format.<|im_end|>
            <|im_start|>user
            {html}<|im_end|>
            <|im_start|>assistant{incomplete_md}"""
