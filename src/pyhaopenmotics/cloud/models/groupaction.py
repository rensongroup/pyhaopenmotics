"""Groupaction Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .location import Location  # noqa: TC001


@dataclass
class GroupAction(DataClassORJSONMixin):
    """Object holding an OpenMotics GroupAction.

    # noqa: E800
    # {
    # "_version": <version>,
    # "actions": [
    #     <action type>, <action number>,
    #     <action type>, <action number>,
    #     ...
    # ],
    # "id": <id>,
    # "location": {
    #     "installation_id": <installation id>
    # },
    # "name": "<name>"
    # }
    """

    idx: int = field(metadata=field_options(alias="id"))
    local_id: int | None = field(default=None)
    name: str | None = field(default=None)
    actions: list[Any] | None = field(default=None)
    location: Location | None = field(default=None)
    version: str | None = field(
        default=None,
        metadata=field_options(alias="_version"),
    )

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
