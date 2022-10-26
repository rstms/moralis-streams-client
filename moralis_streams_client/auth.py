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


class SignatureCheckMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, signature):
        super().__init__(app)
        self.signature = signature

    async def set_cached_receive(self, request):
        cached = await request._receive()

        async def receive():
            return cached

        request._receive = receive

    async def dispatch(self, request, call_next):

        if request.scope["path"] in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        if (
            self.signature is None
            or self.signature.header is None
            or self.signature.key is None
        ):
            msg = "signature validator not configured"
            critical(f"{msg}: {request.url=}")
            return PlainTextResponse(
                msg, status_code=codes.INTERNAL_SERVER_ERROR
            )

        request_signature = request.headers.get(self.signature.header, None)
        if request_signature is None:
            msg = "missing signature"
            error(f"{msg}: {request.url=}")
            return PlainTextResponse(msg, status_code=codes.BAD_REQUEST)
        else:
            # ensure calls to request.receive() will return cached result
            await self.set_cached_receive(request)
            body = await request.body()
            debug(
                f"validating: {request.url} type={type(body)} length={len(body)} {request_signature}"
            )
            if not self.signature.validate(request_signature, body):
                msg = "authorization failed"
                error(f"{msg}: {request.url=}")
                return PlainTextResponse(msg, status_code=codes.UNAUTHORIZED)

        response = await call_next(request)

        return response
