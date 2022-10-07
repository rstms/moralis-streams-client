"""Top-level package for moralis-streams-client."""

from .auth import verify_signature
from .cli import cli
from .version import __author__, __email__, __timestamp__, __version__

__all__ = [
    __version__,
    __timestamp__,
    __author__,
    __email__,
    "cli",
    "verify_signature",
]
