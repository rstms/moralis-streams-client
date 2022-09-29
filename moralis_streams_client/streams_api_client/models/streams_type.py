from enum import Enum


class StreamsType(str, Enum):
    WALLET = "wallet"
    CONTRACT = "contract"

    def __str__(self) -> str:
        return str(self.value)
