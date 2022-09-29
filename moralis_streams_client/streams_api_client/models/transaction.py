from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Transaction")


@attr.s(auto_attribs=True)
class Transaction:
    """
    Attributes:
        tag (str):
        stream_id (str):
        stream_type (str):
        hash_ (str):
        transaction_index (str):
        from_address (str):
        gas (Optional[str]):
        gas_price (Optional[str]):
        nonce (Optional[str]):
        input_ (Optional[str]):
        to_address (Optional[str]):
        value (Optional[str]):
        type (Optional[str]):
        v (Optional[str]):
        r (Optional[str]):
        s (Optional[str]):
        receipt_cumulative_gas_used (Optional[str]):
        receipt_gas_used (Optional[str]):
        receipt_contract_address (Optional[str]):
        receipt_root (Optional[str]):
        receipt_status (Optional[str]):
    """

    tag: str
    stream_id: str
    stream_type: str
    hash_: str
    transaction_index: str
    from_address: str
    gas: Optional[str]
    gas_price: Optional[str]
    nonce: Optional[str]
    input_: Optional[str]
    to_address: Optional[str]
    value: Optional[str]
    type: Optional[str]
    v: Optional[str]
    r: Optional[str]
    s: Optional[str]
    receipt_cumulative_gas_used: Optional[str]
    receipt_gas_used: Optional[str]
    receipt_contract_address: Optional[str]
    receipt_root: Optional[str]
    receipt_status: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        tag = self.tag
        stream_id = self.stream_id
        stream_type = self.stream_type
        hash_ = self.hash_
        transaction_index = self.transaction_index
        from_address = self.from_address
        gas = self.gas
        gas_price = self.gas_price
        nonce = self.nonce
        input_ = self.input_
        to_address = self.to_address
        value = self.value
        type = self.type
        v = self.v
        r = self.r
        s = self.s
        receipt_cumulative_gas_used = self.receipt_cumulative_gas_used
        receipt_gas_used = self.receipt_gas_used
        receipt_contract_address = self.receipt_contract_address
        receipt_root = self.receipt_root
        receipt_status = self.receipt_status

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "tag": tag,
                "streamId": stream_id,
                "streamType": stream_type,
                "hash": hash_,
                "transactionIndex": transaction_index,
                "fromAddress": from_address,
                "gas": gas,
                "gasPrice": gas_price,
                "nonce": nonce,
                "input": input_,
                "toAddress": to_address,
                "value": value,
                "type": type,
                "v": v,
                "r": r,
                "s": s,
                "receiptCumulativeGasUsed": receipt_cumulative_gas_used,
                "receiptGasUsed": receipt_gas_used,
                "receiptContractAddress": receipt_contract_address,
                "receiptRoot": receipt_root,
                "receiptStatus": receipt_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tag = d.pop("tag")

        stream_id = d.pop("streamId")

        stream_type = d.pop("streamType")

        hash_ = d.pop("hash")

        transaction_index = d.pop("transactionIndex")

        from_address = d.pop("fromAddress")

        gas = d.pop("gas")

        gas_price = d.pop("gasPrice")

        nonce = d.pop("nonce")

        input_ = d.pop("input")

        to_address = d.pop("toAddress")

        value = d.pop("value")

        type = d.pop("type")

        v = d.pop("v")

        r = d.pop("r")

        s = d.pop("s")

        receipt_cumulative_gas_used = d.pop("receiptCumulativeGasUsed")

        receipt_gas_used = d.pop("receiptGasUsed")

        receipt_contract_address = d.pop("receiptContractAddress")

        receipt_root = d.pop("receiptRoot")

        receipt_status = d.pop("receiptStatus")

        transaction = cls(
            tag=tag,
            stream_id=stream_id,
            stream_type=stream_type,
            hash_=hash_,
            transaction_index=transaction_index,
            from_address=from_address,
            gas=gas,
            gas_price=gas_price,
            nonce=nonce,
            input_=input_,
            to_address=to_address,
            value=value,
            type=type,
            v=v,
            r=r,
            s=s,
            receipt_cumulative_gas_used=receipt_cumulative_gas_used,
            receipt_gas_used=receipt_gas_used,
            receipt_contract_address=receipt_contract_address,
            receipt_root=receipt_root,
            receipt_status=receipt_status,
        )

        return transaction
