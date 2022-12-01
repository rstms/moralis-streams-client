from pathlib import Path

from starlette.config import Config
from starlette.datastructures import Secret

from . import defaults

# load variables from .env if it exists
config = Config(".env")

DEBUG = config("WEBHOOK_DEBUG", cast=bool, default=False)

ADDR = config("WEBHOOK_ADDR", cast=str, default="0.0.0.0")
PORT = config("WEBHOOK_PORT", cast=int, default=8080)

LOG_FILE = config("WEBHOOK_LOG_FILE", cast=str, default=None)
LOG_FILE_MODE = config("WEBHOOK_LOG_FILE_MODE", cast=str, default="a")
LOG_LEVEL = config("WEBHOOK_LOG_LEVEL", cast=str, default="WARNING")
LOG_FORMAT = config(
    "WEBHOOK_LOG_FORMAT", cast=str, default=defaults.LOG_FORMAT
)

ACCESS_LOG_FORMAT = config(
    "WEBHOOK_ACCESS_LOG_FORMAT", cast=str, default=defaults.ACCESS_LOG_FORMAT
)

BUFFER_ENABLE = config("WEBHOOK_BUFFER_ENABLE", cast=bool, default=True)

RELAY_URL = config("WEBHOOK_RELAY_URL", cast=str, default=None)
RELAY_HEADER = config("WEBHOOK_RELAY_HEADER", default="X-API-Key")
RELAY_ID_HEADER = config("WEBHOOK_RELAY_ID_HEADER", default="X-Relay-ID")
RELAY_KEY = config("WEBHOOK_RELAY_KEY", cast=Secret)

API_KEY = config("WEBHOOK_API_KEY", cast=Secret)

TUNNEL = config("WEBHOOK_TUNNEL", cast=bool, default=True)
NGROK_AUTHTOKEN = config("NGROK_AUTHTOKEN", cast=Secret)

MAX_CONTENT_SIZE = config(
    "WEBHOOK_MAX_CONTENT_SIZE", cast=int, default=10_000_000
)

MORALIS_API_KEY = config("MORALIS_API_KEY", cast=Secret)
MORALIS_STREAMS_API_DEBUG = config(
    "MORALIS_STREAMS_API_DEBUG", cast=bool, default=False
)
MORALIS_STREAMS_API_PROTOCOL_PATCH = config(
    "MORALIS_STREAMS_API_PROTOCOL_PATCH", cast=bool, default=False
)
