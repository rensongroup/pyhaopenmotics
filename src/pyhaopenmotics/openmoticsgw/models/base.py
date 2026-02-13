"""Base Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class OpenMoticsBase(DataClassORJSONMixin):
    """Base class for OpenMotics models."""

    idx: int = field(metadata=field_options(alias="id"), default=0)
    local_id: int = field(default=0)
    name: str = field(default="None")

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        if d.get("id") is not None and d.get("local_id") is None:
            d["local_id"] = d["id"]
        return d
