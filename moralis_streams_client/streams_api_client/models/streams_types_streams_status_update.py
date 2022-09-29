from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..models.streams_status import StreamsStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="StreamsTypesStreamsStatusUpdate")


@attr.s(auto_attribs=True)
class StreamsTypesStreamsStatusUpdate:
    """
    Attributes:
        status (StreamsStatus): The stream status:
            [active] The Stream is healthy and processing blocks
            [paused] The Stream is paused and is not processing blocks
            [error] The Stream has encountered an error and is not processing blocks
    """

    status: StreamsStatus

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = StreamsStatus(d.pop("status"))

        streams_types_streams_status_update = cls(
            status=status,
        )

        return streams_types_streams_status_update
