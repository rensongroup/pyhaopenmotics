"""Location Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class FloorCoordinates(DataClassORJSONMixin):
    """Class holding the floor_coordinates."""

    x: int = field(default=0)
    y: int = field(default=0)


@dataclass
class Location(DataClassORJSONMixin):
    """Class holding the location."""

    installation_id: int = field(default=0)
    gateway_id: int = field(default=0)
    floor_id: int = field(default=0)
    room_id: int = field(default=0)
    floor_coordinates: FloorCoordinates | None = field(default=None)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        if d.get("room_id") is None and d.get("room") is not None:
            d["room_id"] = d["room"]

        fc = d.get("floor_coordinates")
        if isinstance(fc, dict) and ("x" not in fc or "y" not in fc):
            d["floor_coordinates"] = None
        return d
