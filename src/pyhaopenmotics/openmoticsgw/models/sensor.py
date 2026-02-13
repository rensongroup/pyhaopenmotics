"""Output Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro.mixins.orjson import DataClassORJSONMixin

from .base import OpenMoticsBase
from .location import Location


@dataclass
class Status(DataClassORJSONMixin):
    """Class holding the status."""

    humidity: float = field(default=0.0)
    temperature: float = field(default=0.0)
    brightness: int = field(default=0)


@dataclass
class Sensor(OpenMoticsBase, DataClassORJSONMixin):
    """Class holding an OpenMotics Sensor."""

    # pylint: disable=too-many-instance-attributes
    location: Location | None = field(default=None)
    physical_quantity: str = field(default="None")
    status: Status | None = field(default=None)
    last_state_change: float = field(default=0.0)
    version: str = field(default="0.0")

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = super().__pre_deserialize__(d)
        d["location"] = d.copy()
        return d

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
