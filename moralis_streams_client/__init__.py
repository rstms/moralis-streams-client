"""Top-level package for moralis-streams-client."""

from .api import MoralisStreamsApi
from .auth import Signature
from .cli import cli
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
    "cli",
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
    "Signature",
]
