from mock import patch, mock_open, Mock, MagicMock
import pytest
import llmdy
from llmdy.types import WhisperTranscription, YTInfo


@pytest.fixture(autouse=True)
def before_each():
    llmdy.agents.audio_extractor.Cache = MagicMock()
    llmdy.agents.audio_extractor.Cache.get.return_value = None
    yield


def test_transcription_with_chapters():
    with patch("builtins.open", mock_open()) as m:
        mocked_open: Mock = m
        info: YTInfo = {"chapters": [
            {"title": "Title 1", "start_time": 0.0, "end_time": 1.0},
            {"title": "Title 2", "start_time": 1.0, "end_time": 2.0}
        ], "fulltitle": "Full Title", "uploader": "John Doe"}

        transcription_mock = MagicMock()
        llmdy.agents.audio_extractor.whisper.audio.transcriptions.create = transcription_mock

        return_value: WhisperTranscription = WhisperTranscription()
        return_value.segments = [{
            "start": 0.0,
            "end": 0.5,
            "text": "This is a"
        }, {
            "start": 0.5,
            "end": 0.9,
            "text": " test transcription."
        }, {
            "start": 1.1,
            "end": 1.5,
            "text": "It is meant to mock a real whisper transcription."
        }]

        transcription_mock.return_value = return_value

        audio_transcription = llmdy.agents.audio_extractor.AudioExtractor(
            info=info, file_name="mock.mp3")

        assert audio_transcription.extract_audio(
        ) == f"""## Title 1

This is a test transcription.

## Title 2

It is meant to mock a real whisper transcription.
"""
        mocked_open.assert_called_once_with(
            "mock.mp3", "rb")


def test_transcription():
    with patch("builtins.open", mock_open()) as m:
        mocked_open: Mock = m
        info: YTInfo = {"chapters": [],
                        "fulltitle": "Full Title", "uploader": "John Doe"}

        transcription_mock = MagicMock()
        llmdy.agents.audio_extractor.whisper.audio.transcriptions.create = transcription_mock

        return_value: WhisperTranscription = WhisperTranscription()
        return_value.text = "This is a test transcription. It is meant to mock a real whisper transcription."

        transcription_mock.return_value = return_value

        audio_transcription = llmdy.agents.audio_extractor.AudioExtractor(
            info=info, file_name="mock.mp3")

        assert audio_transcription.extract_audio(
        ) == "This is a test transcription. It is meant to mock a real whisper transcription."
        mocked_open.assert_called_once_with(
            "mock.mp3", "rb")


def test_cached_transcription():
    llmdy.agents.audio_extractor.Cache.get.return_value = "This is a test transcription. It is meant to mock a real whisper transcription."

    with patch("builtins.open", mock_open()) as m:
        mocked_open: Mock = m
        info: YTInfo = {"chapters": [],
                        "fulltitle": "Full Title", "uploader": "John Doe"}

        audio_transcription = llmdy.agents.audio_extractor.AudioExtractor(
            info=info, file_name="mock.mp3")

        assert audio_transcription.extract_audio(
        ) == "This is a test transcription. It is meant to mock a real whisper transcription."
        mocked_open.assert_not_called()
        llmdy.agents.audio_extractor.Cache.insert.assert_not_called()
