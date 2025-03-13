import logging
from typing import Any
import openai
from constants import READERLM_MODEL, READERLM_PROMPT
import argparse
import pydantic
from llmdy.types import YTInfo
from llmdy.util import readerlm
from llmdy.agents.audio_extractor import AudioExtractor
from llmdy.agents.transcript2md import Transcript2Markdown
from llmdy.cache import Cache
from llmdy.recovery import Recovery
import sanitize
import yt_dlp
import hashlib
from llmdy.sanitize import remove_md_block_response

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
# HANDLERS
###########################################


def handle_html(args: Arguments):
    html: str = sanitize.get_html(str(args.url))
    cleaned_html = sanitize.clean_html(
        html, f"{args.url.scheme}://{args.url.host}", True, True)

    if args.output_html:
        with open(f"{args.out}.html", "w+") as f:
            f.write(cleaned_html)

    cached = Cache.get(str(args.url))
    if cached:
        print(cached)
        return

    recovery = Recovery(key=args.out, url=args.url,
                        on_complete_write=(lambda x: remove_md_block_response(x)))
    prompt = READERLM_PROMPT.format(
        html=cleaned_html, incomplete_md=recovery.recover())
    response: openai.Stream[openai.types.Completion] = readerlm.completions.create(
        model=READERLM_MODEL, prompt=prompt, stream=True, stop=["<|im_end|>"])

    with recovery as r:
        for chunk in response:
            chunk = chunk.choices[0].delta["content"] if hasattr(
                chunk.choices[0], 'delta') and chunk.choices[0].delta else chunk.choices[0].text
            if chunk != None:
                r.write(chunk)
                print(chunk, end="")

    logging.info(f"Markdown file has been created successfully: {args.out}.")


def handle_youtube(args: Arguments):
    url = str(args.url)
    cached = Cache.get(url)

    if cached:
        print(cached)
        return

    file_name = hashlib.sha256(str.encode(url)).hexdigest()

    def on_finished(d):
        nonlocal file_name
        if d["status"] == "finished":
            file_name = d["filename"]

    with yt_dlp.YoutubeDL({"progress_hooks": [on_finished], "outtmpl": f"{file_name}.%(ext)s", "extract_audio": True, "format": "bestaudio/best"}) as yt:
        info: YTInfo = yt.extract_info(url, download=False)
        yt.download(url)

    audio_extractor = AudioExtractor(info, file_name)
    incomplete_transcript = audio_extractor.extract_audio()
    transcript2md = Transcript2Markdown(
        incomplete_transcript_md=incomplete_transcript, info=info, file_name=file_name)
    transcript2md.convert()

    # Cache.insert(url, transcription)
    # print(transcription.text)


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
        "--output-html", help="Outputs the parsed HTML, if applicable", required=False, default=False
    )
    args = Arguments.parse(parser.parse_args())

    if "youtube.com" in args.url.host or "youtu.be" in args.url.host:
        handle_youtube(args)
    else:
        handle_html(args)


if __name__ == "__main__":
    main()
