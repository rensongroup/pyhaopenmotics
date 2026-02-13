"""Output Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro.mixins.orjson import DataClassORJSONMixin

from .base import OpenMoticsBase


@dataclass
class Status(DataClassORJSONMixin):
    """Class holding the status."""

    voltage: float = field(default=0.0)
    frequency: float = field(default=0.0)
    current: float = field(default=0.0)
    power: float = field(default=0.0)


@dataclass
class EnergySensor(OpenMoticsBase, DataClassORJSONMixin):
    """Class holding an OpenMotics Energy Sensor."""

    # pylint: disable=too-many-instance-attributes
    status: Status | None = field(default=None)
    inverted: bool = field(default=False)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = super().__pre_deserialize__(d)

        status_list = d.get("status")
        if isinstance(status_list, list):
            d["status"] = {
                "voltage": status_list[0] if len(status_list) > 0 else 0,
                "frequency": status_list[1] if len(status_list) > 1 else 0,
                "current": status_list[2] if len(status_list) > 2 else 0,
                "power": status_list[3] if len(status_list) > 3 else 0,
            }

        return d

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
