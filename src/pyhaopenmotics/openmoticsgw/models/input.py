"""Output Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .base import OpenMoticsBase


@dataclass
class Status(DataClassORJSONMixin):
    """Class holding the status."""

    on: bool = field(default=False)
    locked: bool = field(default=False)
    value: int = field(metadata=field_options(alias="dimmer"), default=0)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        if d.get("status") == 1:
            d["on"] = True
        return d


@dataclass
class OMInput(OpenMoticsBase, DataClassORJSONMixin):
    """Class holding an OpenMotics Input."""

    # pylint: disable=too-many-instance-attributes
    status: Status | None = field(default=None)
    last_state_change: float = field(default=0.0)
    room: int = field(default=0)
    version: str = field(default="0.0")

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = super().__pre_deserialize__(d)
        return d

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
