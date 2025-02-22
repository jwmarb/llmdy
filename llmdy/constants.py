import os
import dotenv

dotenv.load_dotenv("../.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
READERLM_MODEL = os.getenv("READERLM_MODEL")
READERLM_PROMPT = """<|im_start|>Extract the main content from the given HTML and convert it to Markdown format.<|im_end|>
            <|im_start|>user
            {html}<|im_end|>
            <|im_start|>assistant{incomplete_md}"""
