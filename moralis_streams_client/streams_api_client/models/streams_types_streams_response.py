from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import attr

from ..models.streams_model import StreamsModel
from ..types import UNSET, Unset

T = TypeVar("T", bound="StreamsTypesStreamsResponse")


@attr.s(auto_attribs=True)
class StreamsTypesStreamsResponse:
    """
    Attributes:
        result (List[StreamsModel]): Array of project Streams
        total (float): Total count of streams on the project
        cursor (Union[Unset, str]): Cursor for fetching next page
    """

    result: List[StreamsModel]
    total: float
    cursor: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        result = []
        for result_item_data in self.result:
            result_item = result_item_data.to_dict()

            result.append(result_item)

        total = self.total
        cursor = self.cursor

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "result": result,
                "total": total,
            }
        )
        if cursor is not UNSET:
            field_dict["cursor"] = cursor

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        result = []
        _result = d.pop("result")
        for result_item_data in _result:
            result_item = StreamsModel.from_dict(result_item_data)

            result.append(result_item)

        total = d.pop("total")

        cursor = d.pop("cursor", UNSET)

        streams_types_streams_response = cls(
            result=result,
            total=total,
            cursor=cursor,
        )

        return streams_types_streams_response
