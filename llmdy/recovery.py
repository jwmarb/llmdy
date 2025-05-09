from types import TracebackType
from typing import Callable
from llmdy.constants import RECOVERY_STRATEGY, CACHE_TTL
from llmdy.util import rediscli
import os


def __generate_key__(key: str) -> str:
    return f"recovery:{key}"


def __generate_key_prog__(key: str) -> str:
    return f"recovery_prog:{key}"


class Recovery:
    def __init__(self, key: str, url: str, on_complete_write: Callable[[str], str] = (lambda x: x)):
        self._data = ""
        self._file_path = key
        self._on_complete_write = on_complete_write
        match RECOVERY_STRATEGY:
            case 'disk':
                self._key = key
                self._prog_key = f"{key}.tmp"
            case _:
                self._key = __generate_key__(url)
                self._prog_key = __generate_key_prog__(url)

    def __enter__(self):
        self._data: str | None = "" if self._data == None else self._data
        self._file = open(
            self._prog_key, "a+") if RECOVERY_STRATEGY == 'disk' else None

        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None):
        if exc_value is None:
            finalized_md = self._on_complete_write(self._data)

            match RECOVERY_STRATEGY:
                case 'disk':
                    self._file.close()
                    try:
                        os.remove(self._prog_key)
                    except FileNotFoundError as e:
                        pass
                case 'redis':
                    rediscli.delete(self._prog_key)
                    rediscli.setex(self._key, CACHE_TTL, finalized_md)
                case 'none':
                    pass

            with open(self._file_path, "w+") as f:
                f.write(finalized_md)
        else:
            if RECOVERY_STRATEGY == 'disk':
                self._file.close()
        self._data = None

    def write(self, data: str):
        """
        Writes to the data stream. If the recovery strategy is 'disk', it writes to a temporary file. If the recovery strategy is 'redis', it writes to a Redis instance. If the recovery strategy is 'none', it does nothing.
        """
        self._data += data

        match RECOVERY_STRATEGY:
            case 'disk':
                self._file.write(data)
            case 'redis':
                rediscli.setex(self._prog_key, CACHE_TTL, self._data)
            case "none":
                pass

    def get_finalized_data(self) -> str:
        return self._on_complete_write(self._data)

    def recover(self):
        """
        Attempts to recover data from previous process. If there isn't any, a blank string is returned.
        """
        try:
            match RECOVERY_STRATEGY:
                case 'disk':
                    with open(self._prog_key, "r+") as f:
                        self._data = f.read()
                case 'redis':
                    self._data = rediscli.get(self._prog_key).decode('utf-8')
                case "none":
                    pass
            return self._data or ""
        except Exception as e:
            return ""
