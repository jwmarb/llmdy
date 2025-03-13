from typing import TypedDict


class YTChapter(TypedDict):
    title: str
    start_time: float
    end_time: float


class YTInfo(TypedDict):
    chapters: list[YTChapter]
    fulltitle: str
    uploader: str


class WhisperTranscriptionSegment(TypedDict):
    text: str
    start: float
    end: float


class WhisperTranscription:
    segments: list[WhisperTranscriptionSegment]
    text: str
