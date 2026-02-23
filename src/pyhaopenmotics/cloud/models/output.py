"""Output Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .location import Location  # noqa: TC001

zombie_status = {"on": None, "locked": None, "manual_override": None, "value": None}


@dataclass
class Status(DataClassORJSONMixin):
    """Class holding the status."""

    on: bool | None = field(default=None)
    locked: bool | None = field(default=None)
    manual_override: bool | None = field(default=None)
    value: int | None = field(default=None)


@dataclass
class Output(DataClassORJSONMixin):
    """Class holding an OpenMotics Output.

    # noqa: E800
     # [{
     #     'name': 'name1',
     #     'type': 'OUTLET',
     #     'capabilities': ['ON_OFF'],
     #     'location': {'floor_coordinates': {'x': None, 'y': None},
     #          'installation_id': 21,
     #          'gateway_id': 408,
     #          'floor_id': None,
     #          'room_id': None},
     #     'metadata': None,
     #     'status': {'on': False, 'locked': False, 'manual_override': False},
     #     'last_state_change': 1633099611.275243,
     #     'id': 18,
     #     '_version': 1.0
     #     },{
     #     'name': 'name2',
     #     'type': 'OUTLET',
     #     ...
    """

    # pylint: disable=too-many-instance-attributes
    name: str
    idx: int = field(metadata=field_options(alias="id"))
    output_type: str = field(metadata=field_options(alias="type"))
    local_id: int | None = field(default=None)
    location: Location | None = field(default=None)
    capabilities: list[Any] | None = field(default=None)
    metadata: dict[str, Any] | None = field(default=None)
    last_state_change: float | None = field(default=None)
    version: str | None = field(
        default=None,
        metadata=field_options(alias="_version"),
    )
    status: Status | None = field(default=None)

    @classmethod
    def __post_deserialize__(
        cls,
        obj: Output,
    ) -> Output:
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
        return f"{self.idx}_{self.name}_{self.output_type}"
