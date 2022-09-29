from enum import Enum


class StateMutabilityType(str, Enum):
    PURE = "pure"
    VIEW = "view"
    NONPAYABLE = "nonpayable"
    PAYABLE = "payable"

    def __str__(self) -> str:
        return str(self.value)
