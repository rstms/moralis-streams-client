from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="INFTTransfer")


@attr.s(auto_attribs=True)
class INFTTransfer:
    """
    Attributes:
        transaction_hash (str):
        token_address (str):
        log_index (str):
        tag (str):
        token_contract_type (str):
        token_name (str):
        token_symbol (str):
        from_ (str):
        to (str):
        token_id (str):
        amount (str):
        operator (Optional[str]):
    """

    transaction_hash: str
    token_address: str
    log_index: str
    tag: str
    token_contract_type: str
    token_name: str
    token_symbol: str
    from_: str
    to: str
    token_id: str
    amount: str
    operator: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        transaction_hash = self.transaction_hash
        token_address = self.token_address
        log_index = self.log_index
        tag = self.tag
        token_contract_type = self.token_contract_type
        token_name = self.token_name
        token_symbol = self.token_symbol
        from_ = self.from_
        to = self.to
        token_id = self.token_id
        amount = self.amount
        operator = self.operator

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "transactionHash": transaction_hash,
                "tokenAddress": token_address,
                "logIndex": log_index,
                "tag": tag,
                "tokenContractType": token_contract_type,
                "tokenName": token_name,
                "tokenSymbol": token_symbol,
                "from": from_,
                "to": to,
                "tokenId": token_id,
                "amount": amount,
                "operator": operator,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        transaction_hash = d.pop("transactionHash")

        token_address = d.pop("tokenAddress")

        log_index = d.pop("logIndex")

        tag = d.pop("tag")

        token_contract_type = d.pop("tokenContractType")

        token_name = d.pop("tokenName")

        token_symbol = d.pop("tokenSymbol")

        from_ = d.pop("from")

        to = d.pop("to")

        token_id = d.pop("tokenId")

        amount = d.pop("amount")

        operator = d.pop("operator")

        inft_transfer = cls(
            transaction_hash=transaction_hash,
            token_address=token_address,
            log_index=log_index,
            tag=tag,
            token_contract_type=token_contract_type,
            token_name=token_name,
            token_symbol=token_symbol,
            from_=from_,
            to=to,
            token_id=token_id,
            amount=amount,
            operator=operator,
        )

        return inft_transfer
