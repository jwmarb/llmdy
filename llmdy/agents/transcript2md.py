import openai

from llmdy.constants import AGENT_MODEL
from llmdy.recovery import Recovery
from llmdy.llmdy_types import YTInfo
from llmdy.util import agent


class Transcript2Markdown:
    __namespace__ = "transcript2md"
    __system_prompt__ = r"""**Task:** Organize and restructure the provided transcript (wrapped in <|begin_bad_markdown|> tags) into a clean, logical Markdown format. Use the rules below to guide your formatting. Additional context for the transcript is provided in <|begin_context|> tags.  

**Rules to Follow:**  
1. **Group Similar Content**: Cluster related ideas or topics into the same section.  
2. **Separate Unrelated Content**: Divide non-related content into distinct sections with headings.  
3. **Use Headings**: Create clear sections using headers (e.g., `#`, `##`) to improve readability.  
4. **Highlight Key Information**: Bold text (**...**) for critical details and italicize (_..._) for emphasis.  
5. **Organize Lists**:  
   - Use **unordered lists** (`-`, `*`) for non-sequential items.  
   - Use **ordered lists** (`1.`, `2.`) for hierarchical or step-based content.  
6. **Format Code and Tables**:  
   - Wrap **code snippets** in triple backticks (\`\`\`).  
   - Use tables for structured data (e.g., headers and rows).  
7. **Block Quotes**: Use `>` to denote direct quotes.  
8. **Preserve Integrity**: **Do NOT paraphrase or summarize**—retain all original content exactly as provided.  
9. **Output Requirements**:  
   - Only return the raw Markdown within <|begin_output|> tags.  
   - Ensure the final output is well-structured, logical, and easy to read.  

**Final Instructions**:  
- Start with the clearest, most logical structure for the transcript.  
- Follow the rules *exactly* and prioritize information integrity (Rule 8).  
- Avoid adding/removing content; only reorganize and apply formatting.  

Your response should ONLY contain the reformatted Markdown within:  
<|begin_output|>  
...[Your formatted Markdown here]...  
<|end_output|>"""

    __prompt__ = """<|begin_context|><title>{title}</title><uploader>{uploader}</uploader><description>{description}</description><|end_context|><|begin_bad_markdown|>{incomplete_transcript_md}<|end_bad_markdown|>"""

    def __init__(self, incomplete_transcript_md: str, info: YTInfo, file_name: str):
        self._info = info
        self._file_name = file_name
        self._prompt = Transcript2Markdown.__prompt__.format(
            title=info["fulltitle"], uploader=info["uploader"], description=info["description"], incomplete_transcript_md=incomplete_transcript_md)

    def __str__(self):
        return f"{Transcript2Markdown.__namespace__}/{self._file_name}"

    def convert(self):
        recovery = Recovery(
            f"{self._info['fulltitle']} - {self._info['uploader']}.md", self._file_name, on_complete_write=(lambda x: x[x.index('<|begin_output|>') + len('<|begin_output|>'):]))
        completion = agent.completions.create(
            model=AGENT_MODEL, prompt=f"""{Transcript2Markdown.__system_prompt__}{self._prompt}{recovery.recover()}""", stream=True, stop=["<|end_output|>"])

        with recovery as r:
            for chunk in completion:
                chunk = chunk.choices[0].delta["content"] if hasattr(
                    chunk.choices[0], 'delta') and chunk.choices[0].delta else chunk.choices[0].text
                if chunk != None:
                    r.write(chunk)

            return r.get_finalized_data()
