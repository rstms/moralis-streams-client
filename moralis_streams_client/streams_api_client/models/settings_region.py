from enum import Enum


class SettingsRegion(str, Enum):
    US_EAST_1 = "us-east-1"
    US_WEST_2 = "us-west-2"
    EU_CENTRAL_1 = "eu-central-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"

    def __str__(self) -> str:
        return str(self.value)
