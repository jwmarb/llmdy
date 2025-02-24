import sanitizer.sanitizer
from bs4 import BeautifulSoup


def get_html(url: str) -> str:
    """
    Retrieves HTML content from a given URL. This is simply a wrapper to the native Rust implementation

    :param url: The URL from which to retrieve the HTML content.

    :return: The HTML content as a string.
    """
    return sanitizer.get_html(url)


def clean_html(html: str, base_url: str, clean_svg=True, clean_base64=True):
    """
    Cleans the provided HTML content by removing potentially unsafe or unwanted elements to reduce LLM token usage. This simply is a wrapper to the native Rust implementation.

    :param html: The HTML content to be sanitized, provided as a string.
    :param base_url: The URL where this HTML originates from.
    :param clean_svg: A boolean flag indicating whether to clean SVG content. Defaults to True.
    :param clean_base64: A boolean flag indicating whether to clean base64-encoded data. Defaults to True.
    :return: The sanitized HTML content as a string.
    """
    return str(BeautifulSoup(sanitizer.clean_html(html.strip(), clean_svg, clean_base64, base_url))).strip()


def remove_md_block_response(generated: str, incomplete_md: str | None = None) -> str:
    """
    Extracts and returns the HTML content from a markdown block that wraps HTML. This method processes a markdown string that is expected to contain an HTM snippet wrapped within a markdown code block. It removes the markdow headers and returns the plain HTML content. If there is no code header it returns the original markdown content.

    :param generated: The generated content from a large language model
    :param incomplete_md: The generated content from a large language model that was recovered from a file/database
    :return: The extracted HTML content as a string.
    """

    MD_HEADERS = ["```markdown", "```md", "```mkdown", "```mkd"]
    MD_CODE_TRAIL = "```"

    def extract_html(content: str) -> str:
        content = content.strip()
        for header in MD_HEADERS:
            if content.startswith(header):
                if content.count("```") & 1 != 0:
                    return content[len(header) + 1:].strip()
                return content[len(header) + 1:-len(MD_CODE_TRAIL) - 1]
        return content
    if incomplete_md:
        extracted_incomplete_md = extract_html(incomplete_md)
        extracted_generated = extract_html(generated)
        return extracted_incomplete_md + extracted_generated

    return extract_html(generated)
