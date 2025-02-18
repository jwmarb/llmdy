import logging
from typing import Any
import openai
import sanitizer.sanitizer
from constants import OPENAI_API_KEY, OPENAI_BASE_URL, READERLM_MODEL, READERLM_PROMPT
from http import HTTPStatus
import argparse
import pydantic
import sanitizer

###########################################
### ENVIRONMENT
###########################################
client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


###########################################
### TYPE DEFINITIONS
###########################################
class Arguments(pydantic.BaseModel):
    url: pydantic.HttpUrl
    out: str

    def parse(args: Any):
        return Arguments(url=args.url, out=args.out)


# def extract_visible_html(html: str) -> str:
#     html = re.match(BODY_PATTERN, html, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
#     print(html)


###########################################
### MAIN FUNCTION
###########################################
def main():
    parser = argparse.ArgumentParser("llmdy")
    parser.add_argument(
        "url",
        help="The URL to obtain the text from and convert it into markdown.",
    )
    parser.add_argument(
        "--out", "-o", help="The file to output", required=False, default="out.md"
    )
    args = Arguments.parse(parser.parse_args())

    html: str = sanitizer.get_html(str(args.url))
    cleaned_html = sanitizer.clean_html(html, True, True)

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": READERLM_PROMPT.format(html=cleaned_html),
            },
            {"role": "user", "content": cleaned_html},
        ],
        model=READERLM_MODEL,
        stream=True,
    )

    written = ""

    with open(args.out, "w+") as f:
        for chunk in response:
            chunk = chunk.choices[0].delta.content
            if chunk != None:
                written += chunk
                f.write(chunk)

    with open(args.out, "w+") as f:
        f.write(written[len("```markdown") + 1 : -len("```") - 1].strip())

    logging.info(f"Markdown file has been created successfully: {args.out}.")


if __name__ == "__main__":
    main()
