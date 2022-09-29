from enum import Enum


class AbiType(str, Enum):
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    EVENT = "event"
    FALLBACK = "fallback"

    def __str__(self) -> str:
        return str(self.value)
