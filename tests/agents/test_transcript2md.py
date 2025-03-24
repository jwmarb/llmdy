from mock import MagicMock, patch
import llmdy.agents.transcript2md
from llmdy.llmdy_types import YTInfo


@patch('llmdy.agents.transcript2md.agent.completions.create')
@patch('builtins.open')
def test_convert(mock_open: MagicMock, mock_create: MagicMock):
    info: YTInfo = {
        "uploader": "uploader",
        "chapters": [],
        "description": "description",
        "fulltitle": "fulltitle"
    }

    mock_open.return_value.__enter__.return_value.read.return_value = ""

    def c(content: str):
        completion = MagicMock()
        completion.choices = [MagicMock()]
        completion.choices[0].delta = {"content": content}
        return completion

    def tokenize(s: str):
        tokens: list[str] = []
        for i in range(0, len(s), 3):
            tokens.append(s[i:min(i+3, len(s))])

        return tokens

    mock_create.return_value = [c(token) for token in tokenize(
        "<|begin_output|># Full Title\nHello World")]

    transcript2md = llmdy.agents.transcript2md.Transcript2Markdown(
        "hello world", info, file_name="file")

    assert str(transcript2md) == 'transcript2md/file'

    results: str = transcript2md.convert()

    assert results == "# Full Title\nHello World"
