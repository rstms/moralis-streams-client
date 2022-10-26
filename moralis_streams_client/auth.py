# Signature checking middleware

import json
import logging

from fastapi import HTTPException
from requests import codes
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

from .signature import Signature

logger = logging.getLogger(__name__)
debug = logger.debug
error = logger.error
critical = logger.critical


class SignatureValidator:
    signature = None

    def __init__(self, signature):
        self.__class__.signature = signature

    async def set_cached_receive(self, request):
        cached = await request._receive()

        async def receive():
            return cached

        request._receive = receive
