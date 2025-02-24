"""ventilation Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

######################################################################################
#
# To be done
# I have no access to an environment with ventilatiosn
#
######################################################################################

zombie_groupstatus = {
    "state": False,
    "mode": None,
}

zombie_unitstatus = {
    "state": None,
    "setpoint": None,
    "steering_power": None,
    "active_preset": None,
    "current_temperature": None,
    "mode": None,
    "preset_expiration": None,
    "actual_temperature": None,
    "current_setpoint": None,
    "preset": None,
}


@dataclass
class GroupLocation(DataClassORJSONMixin):
    """Class holding the location."""

    ventilation_group_id: int | None = field(default=None)
    installation_id: int | None = field(default=None)
    room_id: int | None = field(default=None)


@dataclass
class UnitLocation(DataClassORJSONMixin):
    """Class holding the location."""

    ventilation_group_id: int | None = field(default=None)
    installation_id: int | None = field(default=None)
    room_id: int | None = field(default=None)


@dataclass
class GroupStatus(DataClassORJSONMixin):
    """Class holding the status."""

    mode: str | None = field(default=None)
    state: bool | None = field(default=None)


@dataclass
class UnitStatus(DataClassORJSONMixin):
    """Class holding the status."""

    state: str | None = field(default=None)
    setpoint: float | None = field(default=None)
    steering_power: float | None = field(default=None)
    active_preset: str | None = field(default=None)
    current_temperature: float | None = field(default=None)
    mode: str | None = field(default=None)
    preset_expiration: str | None = field(default=None)
    actual_temperature: float | None = field(default=None)
    current_setpoint: float | None = field(default=None)
    preset: str | None = field(default=None)


@dataclass
class Presets(DataClassORJSONMixin):
    """Class holding the status."""

    away: str | None = field(default=None)
    party: str | None = field(default=None)
    vacation: str | None = field(default=None)


@dataclass
class Schedule(DataClassORJSONMixin):
    """Class holding the schedule."""

    data: dict[str, Any] | None = field(default=None)
    start: str | None = field(default=None)


@dataclass
class ConfigurationPreset(DataClassORJSONMixin):
    """Class holding the configuration presets."""

    output_0_id: int | None = field(default=None)
    output_1_id: int | None = field(default=None)
    presets: Presets | None = field(default=None)
    schedule: Schedule | None = field(default=None)
    sensor_id: int | None = field(default=None)


@dataclass
class Configuration(DataClassORJSONMixin):
    """Class holding the configuration."""

    heating: ConfigurationPreset | None = field(default=None)
    cooling: ConfigurationPreset | None = field(default=None)


@dataclass
class Allowed(DataClassORJSONMixin):
    """Object holding allowed."""

    allowed: bool | None = field(default=None)


@dataclass
class Acl(DataClassORJSONMixin):
    """Object holding an acl."""

    set_state: Allowed | None = field(default=None)
    set_mode: Allowed | None = field(default=None)


@dataclass
class VentilationGroup(DataClassORJSONMixin):
    """Class holding an OpenMotics ventilationGroup .

        # noqa: E800
    #  {
    #     "_acl": <acl>,
    #     "_version": <version>,
    #     "schedule": {
    #         "<optional timestamp>": "AUTO|AWAY|PARTY|VACATION",
    #         ...
    #     },
    #     "status": {
    #         "mode": "HEATING|COOLING",
    #         "state": "ON|OFF"
    #     },
    #     "capabilities": ["HEATING", "COOLING"]
    # }

    """

    # pylint: disable=too-many-instance-attributes
    idx: int = field(metadata=field_options(alias="id"))
    local_id: int
    name: str
    schedule: Schedule | None = field(default=None)
    capabilities: list[Any] | None = field(default=None)
    version: str | None = field(
        default=None,
        metadata=field_options(alias="_version"),
    )
    ventilation_ids: list[Any] | None = field(default=None)
    status: GroupStatus | None = field(default=None)
    acl: Acl | None = field(
        default=None,
        metadata=field_options(alias="_acl"),
    )

    @classmethod
    def __post_deserialize__(
        cls,
        obj: VentilationGroup,
    ) -> VentilationGroup:
        """Post deserialize hook for ventilationUnit object."""
        if not obj.status:
            obj.status = GroupStatus.from_dict(zombie_groupstatus)
        return obj

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"


@dataclass
class VentilationUnit(DataClassORJSONMixin):
    """Class holding an OpenMotics ventilationUnit.

    # noqa: E800
    # {
    #     "_version": <version>,
    #     "configuration": {
    #         "heating": {
    #             "output_0_id": <first output id>,
    #             "output_1_id": null | <second output id>,
    #             "presets": {`
    #                 "AWAY": <away temperature>,
    #                 "PARTY": <party temperature>,
    #                 "VACATION": <vacation temperature>
    #             },
    #             "schedule": {
    #                 "data": [
    #                     {
    #                         "0": <temperature from this timestamp>,
    #                         "23400": <temperature from this timestamp>,
    #                         "30600": <temperature from this timestamp>,
    #                         "61200": <temperature from this timestamp>,
    #                         "84600": <temperature from this timestamp>
    #                     },
    #                     ...
    #                 ],
    #                 "start": <timestamp on which schedule needs to be based>
    #             },
    #             "sensor_id": <room sensor id>
    #         },
    #         "cooling": {
    #             "output_0_id": <first output id>,
    #             "output_1_id": null | <second output id>,
    #             "presets": {
    #                 "AWAY": <away temperature>,
    #                 "PARTY": <party temperature>,
    #                 "VACATION": <vacation temperature>
    #             },
    #             "schedule": {
    #                 "data": [
    #                     {
    #                         "0": <temperature from this timestamp>,
    #                         "23400": <temperature from this timestamp>,
    #                         "30600": <temperature from this timestamp>,
    #                         "61200": <temperature from this timestamp>,
    #                         "84600": <temperature from this timestamp>
    #                     },
    #                     ...
    #                 ],
    #                 "start": <timestamp on which schedule needs to be based>
    #             },
    #             "sensor_id": <room sensor id>
    #         }
    #     },
    #     "id": <id>,
    #     "location": {
    #         "installation_id": <installation id>,
    #         "room_id": null | <room id>,
    #         "ventilation_group_id": <ventilation group id>
    #     },
    #     "name": "<name>",
    #     "status": {
    #           "state":"ON",
    #           "setpoint":13.0,
    #           "steering_power":0,
    #           "active_preset":"AUTO",
    #           "current_temperature":18.5,
    #           "mode":"HEATING",
    #           "preset_expiration":null,
    #           "actual_temperature":18.5,
    #           "current_setpoint":13.0,
    #           "preset":"AUTO"},
    # #     }
    # }
    """

    # pylint: disable=too-many-instance-attributes
    name: str
    idx: int = field(metadata=field_options(alias="id"))
    local_id: int | None = field(default=None)
    location: UnitLocation | None = field(default=None)
    status: UnitStatus | None = field(default=None)
    version: str | None = field(
        default=None,
        metadata=field_options(alias="_version"),
    )

    @classmethod
    def __post_deserialize__(
        cls,
        obj: VentilationUnit,
    ) -> VentilationUnit:
        """Post deserialize hook for ventilationUnit object."""
        if not obj.status:
            obj.status = UnitStatus.from_dict(zombie_unitstatus)
        return obj

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
