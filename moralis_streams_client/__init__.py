"""Client module for the Moralis Streams API, including a CLI and a webhook utility for buffering and forwarding endpoint callbacks."""

from .api import MoralisStreamsApi
from .defaults import ACTIVE, ERROR, PAUSED, REGION_CHOICES, STATUS_CHOICES
from .exceptions import (
    MoralisStreamsCallFailed,
    MoralisStreamsError,
    MoralisStreamsErrorReturned,
    MoralisStreamsResponseFormatError,
)
from .version import __author__, __email__, __timestamp__, __version__

__all__ = [
    __version__,
    __timestamp__,
    __author__,
    __email__,
    "ACTIVE",
    "PAUSED",
    "ERROR",
    "REGION_CHOICES",
    "STATUS_CHOICES",
    "MoralisStreamsError",
    "MoralisStreamsCallFailed",
    "MoralisStreamsErrorReturned",
    "MoralisStreamsResponseFormatError",
    "MoralisStreamsApi",
]
