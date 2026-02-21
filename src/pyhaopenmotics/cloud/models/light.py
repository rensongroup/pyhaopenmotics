"""Light Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

if TYPE_CHECKING:
    from .location import Location


@dataclass
class Status(DataClassORJSONMixin):
    """Class holding the status."""

    on: bool
    locked: bool | None = field(default=None)
    manual_override: bool | None = field(default=None)
    value: int | None = field(default=None)


@dataclass
class Light(DataClassORJSONMixin):
    """Class holding an OpenMotics Light.

    # noqa: E800
    #      # {
    #     "_version": <version>,
    #     "capabilities": [
    #         "ON_OFF|RANGE|WHITE_TEMP|FULL_COLOR"
    #     ],
    #     "id": <id>,
    #     "location": {
    #         "floor_coordinates": {
    #             "x": <x coordinate>,
    #             "y": <y coordinate>
    #         },
    #         "floor_id": <floor id>,
    #         "installation_id": <installation id>,
    #         "room_id": <room id>
    #     },
    #     "name": "<name>",
    #     "status": {
    #         "on": true|false
    #     },
    # }
     #     ...
    """

    # pylint: disable=too-many-instance-attributes
    idx: int = field(metadata=field_options(alias="id"))
    local_id: int | None = field(default=None)
    name: str | None = field(default=None)
    capabilities: list[Any] | None = field(default=None)
    location: Location | None = field(default=None)
    status: Status | None = field(default=None)
    version: str | None = field(
        default=None,
        metadata=field_options(alias="_version"),
    )

    _brightness: int | None = field(default=None)

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
