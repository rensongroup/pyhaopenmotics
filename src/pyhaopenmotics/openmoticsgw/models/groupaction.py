"""Groupaction Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from mashumaro.mixins.orjson import DataClassORJSONMixin

from .base import OpenMoticsBase

if TYPE_CHECKING:
    from .location import Location


@dataclass
class GroupAction(OpenMoticsBase, DataClassORJSONMixin):
    """Class holding an OpenMotics GroupAction."""

    # pylint: disable=too-many-instance-attributes
    actions: list[Any] = field(default_factory=lambda: [""])
    location: Location | None = field(default=None)
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
