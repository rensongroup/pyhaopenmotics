"""Output Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .base import OpenMoticsBase


@dataclass
class GroupLocation(DataClassORJSONMixin):
    """Class holding the location."""

    thermostat_group_id: int = field(default=0)
    installation_id: int = field(default=0)
    room_id: int = field(default=0)


@dataclass
class UnitLocation(DataClassORJSONMixin):
    """Class holding the location."""

    thermostat_group_id: int = field(default=0)
    installation_id: int = field(default=0)
    room_id: int = field(default=0)


@dataclass
class GroupStatus(DataClassORJSONMixin):
    """Class holding the status."""

    mode: str = field(default="None")
    state: bool = field(default=False)


@dataclass
class UnitStatus(DataClassORJSONMixin):
    """Class holding the status."""

    actual_temperature: float = field(default=0.0)
    current_setpoint: float = field(metadata=field_options(alias="setpoint_temperature"), default=0.0)
    output_0: str = field(default="None")
    output_1: str = field(default="None")
    preset: str = field(default="None")


@dataclass
class Presets(DataClassORJSONMixin):
    """Class holding the status."""

    away: str = field(default="None")
    party: str = field(default="None")
    vacation: str = field(default="None")


@dataclass
class Schedule(DataClassORJSONMixin):
    """Class holding the Schedule."""

    data: dict[str, Any] = field(default_factory=dict)
    start: str = field(default="None")

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        if "data" not in d:
            d["data"] = {}
        return d


@dataclass
class ConfigurationPreset(DataClassORJSONMixin):
    """Class holding the ConfigurationPreset."""

    output_0_id: int = field(default=0)
    output_1_id: int = field(default=0)
    presets: Presets | None = field(default=None)
    schedule: Schedule | None = field(default=None)
    sensor_id: int = field(default=0)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d["presets"] = d.copy()
        d["schedule"] = d.copy()
        return d


@dataclass
class Allowed(DataClassORJSONMixin):
    """Class holding the Configuration."""

    allowed: bool = field(default=False)


@dataclass
class Acl(DataClassORJSONMixin):
    """Class holding the Acl."""

    set_state: Allowed | None = field(default=None)
    set_mode: Allowed | None = field(default=None)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d["set_state"] = d.copy()
        d["set_mode"] = d.copy()
        return d


@dataclass
class Configuration(DataClassORJSONMixin):
    """Class holding the Configuration."""

    heating: ConfigurationPreset | None = field(default=None)
    cooling: ConfigurationPreset | None = field(default=None)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d["heating"] = d.copy()
        d["cooling"] = d.copy()
        return d


@dataclass
class ThermostatGroup(OpenMoticsBase, DataClassORJSONMixin):
    """Class holding an OpenMotics ThermostatGroup."""

    # pylint: disable=too-many-instance-attributes
    schedule: Schedule | None = field(default=None)
    capabilities: list[Any] = field(default_factory=lambda: ["None"])
    version: str = field(default="0.0")
    thermostat_ids: dict[str, Any] = field(default_factory=lambda: {"ids": "None"})
    status: GroupStatus | None = field(default=None)
    acl: Acl | None = field(default=None)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = super().__pre_deserialize__(d)
        d["schedule"] = d.copy()
        d["acl"] = d.copy()
        return d

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"


@dataclass
class ThermostatUnit(OpenMoticsBase, DataClassORJSONMixin):
    """Class holding an OpenMotics ThermostatUnit."""

    # pylint: disable=too-many-instance-attributes
    location: UnitLocation | None = field(default=None)
    status: UnitStatus | None = field(default=None)
    version: str = field(default="0.0")
    acl: Acl | None = field(default=None)

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = super().__pre_deserialize__(d)
        d["location"] = d.copy()
        d["acl"] = d.copy()
        return d

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
