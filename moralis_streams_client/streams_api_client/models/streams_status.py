from enum import Enum


class StreamsStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"

    def __str__(self) -> str:
        return str(self.value)
