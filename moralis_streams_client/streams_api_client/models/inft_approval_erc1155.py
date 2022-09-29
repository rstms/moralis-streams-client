from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="INFTApprovalERC1155")


@attr.s(auto_attribs=True)
class INFTApprovalERC1155:
    """
    Attributes:
        transaction_hash (str):
        token_address (str):
        log_index (str):
        tag (str):
        account (str):
        operator (str):
        approved (bool):
        token_contract_type (str):
        token_name (str):
        token_symbol (str):
    """

    transaction_hash: str
    token_address: str
    log_index: str
    tag: str
    account: str
    operator: str
    approved: bool
    token_contract_type: str
    token_name: str
    token_symbol: str

    def to_dict(self) -> Dict[str, Any]:
        transaction_hash = self.transaction_hash
        token_address = self.token_address
        log_index = self.log_index
        tag = self.tag
        account = self.account
        operator = self.operator
        approved = self.approved
        token_contract_type = self.token_contract_type
        token_name = self.token_name
        token_symbol = self.token_symbol

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "transactionHash": transaction_hash,
                "tokenAddress": token_address,
                "logIndex": log_index,
                "tag": tag,
                "account": account,
                "operator": operator,
                "approved": approved,
                "tokenContractType": token_contract_type,
                "tokenName": token_name,
                "tokenSymbol": token_symbol,
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

        account = d.pop("account")

        operator = d.pop("operator")

        approved = d.pop("approved")

        token_contract_type = d.pop("tokenContractType")

        token_name = d.pop("tokenName")

        token_symbol = d.pop("tokenSymbol")

        inft_approval_erc1155 = cls(
            transaction_hash=transaction_hash,
            token_address=token_address,
            log_index=log_index,
            tag=tag,
            account=account,
            operator=operator,
            approved=approved,
            token_contract_type=token_contract_type,
            token_name=token_name,
            token_symbol=token_symbol,
        )

        return inft_approval_erc1155
