# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2022-10-16T17:59:39+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field


class VBaseModel(BaseModel):
    class Config:
        extra = Extra.forbid
        json_encoders = {"UUIDModel": lambda b: str(b.__root__)}


class UUIDModel(VBaseModel):
    __root__: UUID = Field(
        ...,
        description="Stringified UUIDv4.\nSee [RFC 4112](https://tools.ietf.org/html/rfc4122)",
    )


class Block(VBaseModel):

    number: str
    hash: str
    timestamp: str


class Log(VBaseModel):

    logIndex: str
    transactionHash: str
    address: str
    data: str
    topic0: str
    topic1: str
    topic2: str
    topic3: str


class Transaction(VBaseModel):

    hash: str
    gas: str
    gasPrice: str
    nonce: str
    input: str
    transactionIndex: str
    fromAddress: str
    toAddress: str
    value: str
    type: str
    v: str
    r: str
    s: str
    receiptCumulativeGasUsed: str
    receiptGasUsed: str
    receiptContractAddress: str
    receiptRoot: str
    receiptStatus: str


class InternalTransaction(VBaseModel):

    from_: str = Field(..., alias="from")
    to: str
    value: str
    transactionHash: str
    gas: str


class AbiInput(VBaseModel):

    name: str
    type: str
    indexed: Optional[bool] = None
    components: Optional[List[AbiInput]] = None
    internalType: Optional[str] = None


class AbiOutput(VBaseModel):

    name: str
    type: str
    components: Optional[List[AbiOutput]] = None
    internalType: Optional[str] = None


class AbiItem(VBaseModel):

    anonymous: Optional[bool] = None
    constant: Optional[bool] = None
    inputs: Optional[List[AbiInput]] = None
    name: Optional[str] = None
    outputs: Optional[List[AbiOutput]] = None
    payable: Optional[bool] = None
    stateMutability: Optional[str] = None
    type: str
    gas: Optional[float] = None


class HistoryModel(VBaseModel):

    id: UUIDModel
    date: datetime
    payload: Optional[IWebhookUnParsed] = None
    tinyPayload: ITinyPayload
    errorMessage: str
    webhookUrl: str
    streamId: str
    tag: str


class SettingsRegion(Enum):
    us_east_1 = "us-east-1"
    us_west_2 = "us-west-2"
    eu_central_1 = "eu-central-1"
    ap_southeast_1 = "ap-southeast-1"


class StreamsStatus(Enum):
    active = "active"
    paused = "paused"
    error = "error"
    terminated = "terminated"


class StreamsFilter(VBaseModel):
    pass


class AdvancedOptions(VBaseModel):

    topic0: str
    filter: Optional[StreamsFilter] = None
    includeNativeTxs: Optional[bool] = None


class StreamsModel(VBaseModel):

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
    id: UUIDModel = Field(..., description="The unique uuid of the stream")
    status: StreamsStatus = Field(..., description="The status of the stream.")
    statusMessage: str = Field(
        ..., description="Description of current status of stream."
    )


class Addresses(VBaseModel):

    address: str = Field(..., description="Address")


AbiInput.update_forward_refs()
AbiOutput.update_forward_refs()


class IWebhookUnParsed(VBaseModel):

    block: Block
    chainId: str
    logs: List[Log]
    txs: List[Transaction]
    txsInternal: List[InternalTransaction]
    abi: List[AbiItem]
    retries: float
    confirmed: bool
    tag: str
    streamId: str


class ITinyPayload(VBaseModel):

    chainId: str
    confirmed: bool
    block: str
    records: float
    retries: float
