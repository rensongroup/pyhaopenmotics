"""Shutter Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .base import OpenMoticsBase
from .location import Location  # noqa: TC001


@dataclass
class Status(DataClassORJSONMixin):
    """Class holding the status."""

    locked: bool = field(default=False)
    manual_override: bool = field(default=False)
    state: str = field(default="None")
    position: int = field(default=0)
    last_change: float = field(default=0.0)
    preset_position: int = field(default=0)


@dataclass
class Attributes(DataClassORJSONMixin):
    """Class holding the Attributes."""

    azimuth: str = field(default="None")
    compass_point: str = field(default="None")
    surface_area: str = field(default="None")


@dataclass
class Metadata(DataClassORJSONMixin):
    """Class holding the Metadata."""

    protocol: str = field(default="None")
    controllable_name: str = field(default="None")


@dataclass
class Shutter(OpenMoticsBase, DataClassORJSONMixin):
    """Object holding an OpenMotics Shutter."""

    # pylint: disable=too-many-instance-attributes
    shutter_type: str = field(metadata=field_options(alias="type"), default="None")
    location: Location | None = field(default=None)
    capabilities: list[str] = field(default_factory=list)
    attributes: Attributes | None = field(default=None)
    metadata: Metadata | None = field(default=None)
    status: Status | None = field(default=None)
    version: str = field(default="0.0")

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = super().__pre_deserialize__(d)
        d["location"] = d.copy()
        d["attributes"] = d.copy()
        d["metadata"] = d.copy()
        return d

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
