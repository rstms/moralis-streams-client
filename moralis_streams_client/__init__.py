"""Top-level package for moralis-streams-client."""

from .api import MoralisStreamsApi
from .defaults import ACTIVE, ERROR, PAUSED, REGION_CHOICES, STATUS_CHOICES
from .exceptions import (
    MoralisStreamsCallFailed,
    MoralisStreamsError,
    MoralisStreamsErrorReturned,
    MoralisStreamsResponseFormatError,
)
from .signature import Signature
from .version import __author__, __email__, __timestamp__, __version__
from .webhook import Webhook

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
    "Signature",
    "Webhook",
]
