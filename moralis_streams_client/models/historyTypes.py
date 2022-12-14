# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2022-10-16T17:59:39+00:00

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field

from .model import HistoryModel, VBaseModel


class HistoryResponse(VBaseModel):

    result: List[HistoryModel]
    cursor: Optional[str] = None
    total: float
