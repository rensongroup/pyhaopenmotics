"""Shutter Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

if TYPE_CHECKING:
    from .location import Location


@dataclass
class Status(DataClassORJSONMixin):
    """Class holding the status."""

    locked: bool | None = field(default=None)
    manual_override: bool | None = field(default=None)
    state: str | None = field(default=None)
    position: int | None = field(default=None)
    last_change: float | None = field(default=None)
    preset_position: int | None = field(default=None)


@dataclass
class Attributes(DataClassORJSONMixin):
    """Class holding the attributes."""

    azimuth: str | None = field(default=None)
    compass_point: str | None = field(default=None)
    surface_area: str | None = field(default=None)
    tilt_angle: int | None = field(default=None)


@dataclass
class Metadata(DataClassORJSONMixin):
    """Class holding the metadata."""

    protocol: str | None = field(default=None)
    controllable_name: str | None = field(default=None)


@dataclass
class Shutter(DataClassORJSONMixin):
    """Object holding an OpenMotics Shutter.

    # noqa: E800
    # {
    # "_version": <version>,
    # "configuration": {
    #     "group_1": null | <group id>,
    #     "group_2": null | <group id>,
    #     "name": "<name>",
    #     "steps": null | <number of steps>,
    #     "timer_down": <timer down>,
    #     "timer_up": <timer up>,
    #     "up_down_config": <up down configuration>
    # },
    # "id": <id>,
    # "capabilities": ["UP_DOWN", "POSITION", "RELATIVE_POSITION",
    #          "HW_LOCK"|"CLOUD_LOCK", "PRESET", "CHANGE_PRESET"],
    # "location": {
    #     "floor_coordinates": {
    #         "x": null | <x coordinate>,
    #         "y": null | <y coordinate>
    #     },
    #     "floor_id": null | <floor id>,
    #     "installation_id": <installation id>,
    #     "room_id": null | <room_id>
    # },
    # "name": "<name>",
    # "status": {
    #     "last_change": <epoch in seconds>
    #     "position": null | <position>,
    #     "state": null | "UP|DOWN|STOP|GOING_UP|GOING_DOWN",
    #     "locked": true | false,
    #     "manual_override": true | false
    # }
    # }
    """

    # pylint: disable=too-many-instance-attributes
    name: str
    idx: int = field(metadata=field_options(alias="id"))
    status: Status
    shutter_type: str = field(metadata=field_options(alias="type"))
    local_id: int | None = field(default=None)
    capabilities: list[str] | None = field(default=None)
    location: Location | None = field(default=None)
    attributes: Attributes | None = field(default=None)
    metadata: Metadata | None = field(default=None)
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
