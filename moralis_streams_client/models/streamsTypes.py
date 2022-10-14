# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2022-10-14T14:39:05+00:00

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field

from .model import AbiItem, AdvancedOptions, StreamsModel, StreamsStatus


class StreamsResponse(BaseModel):
    class Config:
        extra = Extra.forbid

    result: List[StreamsModel] = Field(
        ..., description="Array of project Streams"
    )
    cursor: Optional[str] = Field(
        None, description="Cursor for fetching next page"
    )
    total: float = Field(
        ..., description="Total count of streams on the project"
    )


class StreamsModelCreate(BaseModel):
    class Config:
        extra = Extra.forbid

    webhookUrl: str = Field(
        ...,
        description="Webhook URL where moralis will send the POST request.",
    )
    description: str = Field(..., description="A description for this stream")
    tag: str = Field(
        ...,
        description="A user-provided tag that will be send along the webhook, the user can use this tag to identify the specific stream if multiple streams are present",
    )
    topic0: Optional[List[str]] = Field(
        None,
        description="An Array of topic0's in hex, required if the type : log",
    )
    allAddresses: Optional[bool] = Field(
        None,
        description="Include events for all addresses (only applied when abi and topic0 is provided)",
    )
    includeNativeTxs: Optional[bool] = Field(
        None,
        description="Include or not native transactions defaults to false (only applied when type:contract)",
    )
    includeContractLogs: Optional[bool] = Field(
        None,
        description="Include or not logs of contract interactions defaults to false",
    )
    includeInternalTxs: Optional[bool] = Field(
        None,
        description="Include or not include internal transactions defaults to false",
    )
    abi: Optional[List[AbiItem]] = None
    advancedOptions: Optional[List[AdvancedOptions]] = None
    chainIds: List[str] = Field(
        ...,
        description='The ids of the chains for this stream in hex Ex: ["0x1","0x38"]',
    )


class StreamsStatusUpdate(BaseModel):
    class Config:
        extra = Extra.forbid

    status: StreamsStatus = Field(..., description="The status of the stream.")
