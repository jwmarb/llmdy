from llmdy.cache import Cache
from llmdy.constants import WHISPER_MODEL
from llmdy.util import whisper
from llmdy.types import WhisperTranscription, YTInfo


class AudioExtractor:
    __namespace__ = "audio_extractor"
    __prompt__ = """Title: {title}
Author: {uploader}
Task: You are extracting speech from a transcript. Ignore audio that isn't speech."""

    def __init__(self, info: YTInfo, file_name: str):
        self._info = info
        self._file_name = file_name
        self._prompt = AudioExtractor.__prompt__.format(
            title=info["fulltitle"], uploader=info["uploader"])

    def extract_audio(self) -> str:
        cached = Cache.get(str(self))
        if cached != None:
            return cached

        with open(self._file_name, "rb") as audio_file:
            transcription: WhisperTranscription = whisper.audio.transcriptions.create(
                file=audio_file, prompt=self._prompt, model=WHISPER_MODEL)

        if self._info["chapters"]:
            text = "\n".join([
                f"## {chapter['title']}\n\n"
                f"{''.join([segment['text'] for segment in transcription.segments if round(segment['start'], 2) >= round(chapter['start_time'], 2) and round(segment['end'], 2) <= round(chapter['end_time'], 2)])}\n"
                for chapter in self._info["chapters"]
            ])

            Cache.insert(str(self), text)
            return text

        Cache.insert(str(self), transcription.text)

        return transcription.text

    def __str__(self):
        return f"{AudioExtractor.__namespace__}/{self._file_name}"
