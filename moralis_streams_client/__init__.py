"""Top-level package for moralis-streams-client."""

from .api import API
from .cli import msc
from .version import __author__, __email__, __timestamp__, __version__

__all__ = ["msc", __version__, __timestamp__, __author__, __email__]
