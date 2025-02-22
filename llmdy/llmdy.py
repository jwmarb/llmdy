import logging
import os
from typing import Any
import openai
from constants import OPENAI_API_KEY, OPENAI_BASE_URL, READERLM_MODEL, READERLM_PROMPT
import argparse
import pydantic
import sanitize

###########################################
# ENVIRONMENT
###########################################


client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


###########################################
# TYPE DEFINITIONS
###########################################


class Arguments(pydantic.BaseModel):
    url: pydantic.HttpUrl
    out: str
    output_html: bool

    def parse(args: Any):
        return Arguments(url=args.url, out=args.out, output_html=args.output_html)


###########################################
# MAIN FUNCTION
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
    parser.add_argument(
        "--output-html", help="Outputs the parsed HTML", required=False, default=False
    )
    args = Arguments.parse(parser.parse_args())

    html: str = sanitize.get_html(str(args.url))
    cleaned_html = sanitize.clean_html(html, True, True)

    if args.output_html:
        with open(f"{args.out}.html", "w+") as f:
            f.write(cleaned_html)

    try:
        with open(f"{args.out}.tmp", "r+") as f:
            incomplete_md = f.read()
    except FileNotFoundError:
        incomplete_md = ""
    prompt = READERLM_PROMPT.format(
        html=cleaned_html, incomplete_md=incomplete_md)
    response = client.completions.create(
        model=READERLM_MODEL, prompt=prompt, stream=True, stop=["<|im_end|>"])

    written = ""

    with open(f"{args.out}.tmp", "a+") as f:
        for chunk in response:
            chunk = chunk.choices[0].text
            if chunk != None:
                written += chunk
                f.write(chunk)
                print(written, end="")

    with open(args.out, "w+") as f:
        f.write(sanitize.remove_md_block_response(
            written, incomplete_md=incomplete_md))

    os.remove(f"{args.out}.tmp")

    logging.info(f"Markdown file has been created successfully: {args.out}.")


if __name__ == "__main__":
    main()
