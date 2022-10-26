# streams api client wrapper

import logging
from pprint import pformat

from fastapi import HTTPException, Request
from requests import codes
from starlette.middleware.base import BaseHTTPMiddleware

from . import settings

logger = logging.getLogger("signature")
logger.setLevel("DEBUG")
debug = logger.debug
error = logger.error
critical = logger.critical


async def validate_signature(request: Request):

    signature = request.app.state.signature
    path = request.scope["path"]

    if signature is None or signature.header is None or signature.key is None:
        msg = "signature validator not configured"
        critical(f"{msg}: {path}")
        raise HTTPException(
            detail=msg, status_code=codes.INTERNAL_SERVER_ERROR
        )

    request_signature = request.headers.get(signature.header, None)

    if request_signature is None:
        msg = "missing signature"
        error(f"{msg}: {path}")
        raise HTTPException(detail=msg, status_code=codes.BAD_REQUEST)
    else:
        body = await request.body()
        debug(
            f"validating: {path} type={type(body)} length={len(body)} {request_signature}"
        )
        if not signature.validate(request_signature, body):
            msg = "authorization failed"
            error(f"{msg}: {path}")
            raise HTTPException(detail=msg, status_code=codes.UNAUTHORIZED)
