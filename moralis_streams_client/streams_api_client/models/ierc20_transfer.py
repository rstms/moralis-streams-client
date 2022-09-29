from typing import (
    Any,
    BinaryIO,
    Dict,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="IERC20Transfer")


@attr.s(auto_attribs=True)
class IERC20Transfer:
    """
    Attributes:
        transaction_hash (str):
        token_address (str):
        log_index (str):
        tag (str):
        from_ (str):
        to (str):
        value (str):
        token_decimals (str):
        token_name (str):
        token_symbol (str):
        value_with_decimals (Union[Unset, str]):
    """

    transaction_hash: str
    token_address: str
    log_index: str
    tag: str
    from_: str
    to: str
    value: str
    token_decimals: str
    token_name: str
    token_symbol: str
    value_with_decimals: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        transaction_hash = self.transaction_hash
        token_address = self.token_address
        log_index = self.log_index
        tag = self.tag
        from_ = self.from_
        to = self.to
        value = self.value
        token_decimals = self.token_decimals
        token_name = self.token_name
        token_symbol = self.token_symbol
        value_with_decimals = self.value_with_decimals

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "transactionHash": transaction_hash,
                "tokenAddress": token_address,
                "logIndex": log_index,
                "tag": tag,
                "from": from_,
                "to": to,
                "value": value,
                "tokenDecimals": token_decimals,
                "tokenName": token_name,
                "tokenSymbol": token_symbol,
            }
        )
        if value_with_decimals is not UNSET:
            field_dict["valueWithDecimals"] = value_with_decimals

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        transaction_hash = d.pop("transactionHash")

        token_address = d.pop("tokenAddress")

        log_index = d.pop("logIndex")

        tag = d.pop("tag")

        from_ = d.pop("from")

        to = d.pop("to")

        value = d.pop("value")

        token_decimals = d.pop("tokenDecimals")

        token_name = d.pop("tokenName")

        token_symbol = d.pop("tokenSymbol")

        value_with_decimals = d.pop("valueWithDecimals", UNSET)

        ierc20_transfer = cls(
            transaction_hash=transaction_hash,
            token_address=token_address,
            log_index=log_index,
            tag=tag,
            from_=from_,
            to=to,
            value=value,
            token_decimals=token_decimals,
            token_name=token_name,
            token_symbol=token_symbol,
            value_with_decimals=value_with_decimals,
        )

        return ierc20_transfer
