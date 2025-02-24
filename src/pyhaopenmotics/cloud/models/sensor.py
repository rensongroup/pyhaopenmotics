"""Sensor Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .location import Location

zombie_status = {"humidity": None, "temperature": None, "brightness": None, "power": None}


@dataclass
class Status(DataClassORJSONMixin):
    """Class holding the status."""

    humidity: float | None = field(default=None)
    temperature: float | None = field(default=None)
    brightness: int | None = field(default=None)
    power: float | None = field(default=None)


@dataclass
class Sensor(DataClassORJSONMixin):
    """Class holding an OpenMotics Sensor.

    # noqa: E800
    #     {
    #     "_version": <version>,
    #     "id": <id>,
    #     "name": "<name>",
    #     "location": {
    #         "room_id": null | <room_id>,
    #         "installation_id": <installation id>
    #     },
    #     "status": {
    #         "humidity": null | <hunidity 0 - 100>,
    #         "temperature": null | <temperature -32 - 95>,
    #         "brightness": null | <brightness 0 - 100>
    #     }
    # }
    #     ...
    """

    # pylint: disable=too-many-instance-attributes
    idx: int = field(metadata=field_options(alias="id"))
    name: str
    local_id: int | None = field(default=None)
    location: Location | None = field(default=None)
    physical_quantity: str | None = field(default=None)
    last_state_change: float | None = field(default=None)
    version: str | None = field(
        default=None,
        metadata=field_options(alias="_version"),
    )
    status: Status | None = field(default=None)

    @classmethod
    def __post_deserialize__(
        cls,
        obj: Sensor,
    ) -> Sensor:
        """Post deserialize hook for Output object."""
        if not obj.status:
            obj.status = Status.from_dict(zombie_status)
        return obj

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
