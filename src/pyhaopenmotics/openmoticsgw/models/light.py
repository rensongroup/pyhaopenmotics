"""Output Model for the OpenMotics API."""

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

    on: bool = field(default=False)
    locked: bool = field(default=False)
    manual_override: bool = field(default=False)
    value: int = field(metadata=field_options(alias="dimmer"), default=0)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        if d.get("status") == 1:
            d["on"] = True
        return d


@dataclass
class Light(OpenMoticsBase, DataClassORJSONMixin):
    """Class holding an OpenMotics Light."""

    # pylint: disable=too-many-instance-attributes
    location: Location | None = field(default=None)
    capabilities: list[str] = field(default_factory=lambda: ["ON_OFF"])
    metadata: dict[str, Any] = field(default_factory=dict)
    status: Status | None = field(default=None)
    last_state_change: float = field(default=0.0)
    version: str = field(default="0.0")

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = super().__pre_deserialize__(d)
        d["location"] = d.copy()

        capabilities = ["ON_OFF"]
        if d.get("module_type") == "D":
            capabilities.append("RANGE")
        d["capabilities"] = capabilities

        return d

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
