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

from ..models.settings_region import SettingsRegion
from ..types import UNSET, Unset

T = TypeVar("T", bound="SettingsTypesSettingsModel")


@attr.s(auto_attribs=True)
class SettingsTypesSettingsModel:
    """
    Attributes:
        region (Union[Unset, SettingsRegion]):
    """

    region: Union[Unset, SettingsRegion] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        region: Union[Unset, str] = UNSET
        if not isinstance(self.region, Unset):
            region = self.region.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if region is not UNSET:
            field_dict["region"] = region

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _region = d.pop("region", UNSET)
        region: Union[Unset, SettingsRegion]
        if isinstance(_region, Unset):
            region = UNSET
        else:
            region = SettingsRegion(_region)

        settings_types_settings_model = cls(
            region=region,
        )

        return settings_types_settings_model
