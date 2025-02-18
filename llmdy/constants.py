import os
import dotenv

dotenv.load_dotenv("../.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
READERLM_MODEL = os.getenv("READERLM_MODEL")
READERLM_PROMPT = """Extract the main content from the given HTML and convert it to Markdown format.
            ```html
            {html}```"""
