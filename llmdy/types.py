from typing import TypedDict


class YTChapter(TypedDict):
    title: str
    start_time: float
    end_time: float


class YTInfo(TypedDict):
    chapters: list[YTChapter]
    fulltitle: str
    uploader: str
