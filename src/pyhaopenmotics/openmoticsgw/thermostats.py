"""Module containing the base of an thermostat."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..helpers import merge_dicts
from ..openmoticsgw.models.thermostat import (
    ThermostatGroup,
    ThermostatUnit,
)

if TYPE_CHECKING:
    from ..client.localgateway import LocalGateway  # pylint: disable=R0401


@dataclass
class OpenMoticsThermostats:
    """Object holding information of the OpenMotics thermostats.

    All actions related to thermostats or a specific thermostat.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
        ----
            omcloud: LocalGateway

        """
        self._omcloud = omcloud
        self._thermostat_configs: list[Any] = []

        self.groups = OpenMoticsThermostatGroups(self._omcloud)
        self.units = OpenMoticsThermostatUnits(self._omcloud)

    async def set_mode(
        self,
        mode: str,
    ) -> Any:
        """Set a mode to all Groups the User has access to.

        Args:
        ----
            mode: "HEATING|COOLING"

        Returns:
        -------
            Returns None

        """
        if mode:
            pass

    async def set_state(
        self,
        state: str,
    ) -> Any:
        """Set a mode to all Groups the User has access to.

        Args:
        ----
            state: "ON|OFF"

        Returns:
        -------
            Returns None

        """
        if state:
            pass


class OpenMoticsThermostatGroups:
    """Object holding information of the OpenMotics thermostats.

    All actions related to thermostats or a specific thermostat.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
        ----
            omcloud: LocalGateway

        """
        self._omcloud = omcloud
        self._thermostatgroup_configs: list[Any] = []

    @property
    def thermostatgroup_configs(self) -> list[Any]:
        """Get a list of all thermostat confs.

        Returns
        -------
            list of all thermostatgroup_configs

        """
        return self._thermostatgroup_configs

    @thermostatgroup_configs.setter
    def thermostatgroup_configs(self, thermostatgroup_configs: list[Any]) -> None:
        """Set a list of all thermostat confs.

        Args:
        ----
            thermostatgroup_configs: list

        """
        self._thermostatgroup_configs = thermostatgroup_configs

    async def get_all(
        self,
        thermostatgroup_filter: str | None = None,
    ) -> list[ThermostatGroup]:
        """Get a list of all ThermostatGroup objects.

        Args:
        ----
            thermostatgroup_filter: str

        Returns:
        -------
            Dict with all ThermostatGroup

        """
        if len(self.thermostatgroup_configs) == 0:
            goc = await self._omcloud.exec_action("get_thermostat_group_configurations")
            if goc["success"] is True:
                self.thermostatgroup_configs = goc["config"]

        thermostatgroup_status = await self._omcloud.exec_action("get_thermostat_group_status")
        status = thermostatgroup_status["status"]

        data = merge_dicts(self.thermostatgroup_configs, "status", status)

        thermostatgroups = [ThermostatGroup.from_dict(device) for device in data]

        if thermostatgroup_filter is not None:
            # implemented later
            pass

        return thermostatgroups  # pyright: ignore[reportReturnType]

    async def get_by_id(
        self,
        thermostatgroup_id: int,
    ) -> ThermostatGroup | None:
        """Get thermostat by id.

        Args:
        ----
            thermostatgroup_id: int

        Returns:
        -------
            Returns a thermostatgroup with id

        """
        for thermostatgroup in await self.get_all():
            if thermostatgroup.idx == thermostatgroup_id:
                return thermostatgroup
        return None

    async def set_mode(
        self,
        thermostatgroup_id: int,
        mode: str,
    ) -> Any:
        """Turn on a specified Output object.

        Args:
        ----
            thermostatgroup_id: int
            mode: "HEATING|COOLING"

        Returns:
        -------
            Returns a output with id

        """
        if thermostatgroup_id or mode:
            pass


class OpenMoticsThermostatUnits:
    """Object holding information of the OpenMotics thermostats.

    All actions related to thermostats or a specific thermostat.
    """

    def __init__(self, _omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
        ----
            _omcloud: LocalGateway

        """
        self._omcloud = _omcloud
        self._thermostatunit_configs: list[Any] = []

    @property
    def thermostatunit_configs(self) -> list[Any]:
        """Get a list of all thermostatunit confs.

        Returns
        -------
            list of all thermostatunit_configs

        """
        return self._thermostatunit_configs

    @thermostatunit_configs.setter
    def thermostatunit_configs(self, thermostatunit_configs: list[Any]) -> None:
        """Set a list of all thermostatunit confs.

        Args:
        ----
            thermostatunit_configs: list

        """
        self._thermostatunit_configs = thermostatunit_configs

    async def get_all(
        self,
        thermostatunit_filter: str | None = None,
    ) -> list[ThermostatUnit]:
        """Get a list of all ThermostatUnit objects.

        Args:
        ----
            thermostatunit_filter: str

        Returns:
        -------
            Dict with all ThermostatUnit

        """
        ###############################################################################
        # Code has changed in latest version of gateway:
        #      get_thermostat_configurations does NOT exist anymore
        # As the gateway is now closed source, we cannot see the new functions.
        ###############################################################################
        #
        # Return an empty config to avoid errors
        empty_device = [
            {
                "id": 0,
                "name": "None",
            },
        ]
        return [ThermostatUnit.from_dict(device) for device in empty_device]  # pyright: ignore[reportReturnType]

        # # TO BE FIXED
        # #
        # ###############################################################################
        # if len(self.thermostatunit_configs) == 0:
        #     goc = await self._omcloud.exec_action("get_thermostat_configurations")
        #     if goc["success"] is True:
        #         self.thermostatunit_configs = goc["config"]

        # thermostatunit_status = await self._omcloud.exec_action("get_thermostat_status")
        # status = thermostatunit_status["status"]

        # data = merge_dicts(self.thermostatunit_configs, "status", status)

        # thermostatunits = [ThermostatUnit.from_dict(device) for device in data]

        # if thermostatunit_filter is not None:
        #     # implemented later
        #     pass

        # return thermostatunits

    async def get_by_id(
        self,
        thermostatunit_id: int,
    ) -> ThermostatUnit | None:
        """Get thermostatunit by id.

        Args:
        ----
            thermostatunit_id: int

        Returns:
        -------
            Returns a thermostatunit with id

        """
        for thermostatunit in await self.get_all():
            if thermostatunit.idx == thermostatunit_id:
                return thermostatunit
        return None

    async def set_state(
        self,
        thermostatunit_id: int,
        state: str,
    ) -> Any:
        """Set state of a thermostatunit.

        Args:
        ----
            thermostatunit_id: int
            state: "ON|OFF"

        Returns:
        -------
            Returns a thermostatunit with id

        """
        if thermostatunit_id or state:
            pass

    async def set_temperature(
        self,
        thermostatunit_id: int,
        temperature: float,
    ) -> Any:
        """Set temperature of a thermostatunit.

        Args:
        ----
            thermostatunit_id: int
            temperature: float

        Returns:
        -------
            Returns a thermostatunit with id

        """
        if thermostatunit_id or temperature:
            pass

    async def set_preset(
        self,
        thermostatunit_id: int,
        preset: str,
    ) -> Any:
        """Set preset of a thermostatunit.

        Args:
        ----
            thermostatunit_id: int
            preset: "AUTO|AWAY|PARTY|VACATION"

        Returns:
        -------
            Returns a thermostatunit with id

        """
        if thermostatunit_id or preset:
            pass

    async def set_preset_config(
        self,
        thermostatunit_id: int,
        heating_away_temp: float,
        heating_vacation_temp: float,
        heating_party_temp: float,
        cooling_away_temp: float,
        cooling_vacation_temp: float,
        cooling_party_temp: float,
    ) -> Any:
        """Set preset of a thermostatunit.

        Args:
        ----
            thermostatunit_id: int,
            heating_away_temp: float,
            heating_vacation_temp: float,
            heating_party_temp: float,
            cooling_away_temp: float,
            cooling_vacation_temp: float,
            cooling_party_temp: float,

        Returns:
        -------
            Returns a thermostatunit with id

        """
        payload = {
            "heating": {
                "AWAY": heating_away_temp,
                "VACATION": heating_vacation_temp,
                "PARTY": heating_party_temp,
            },
            "cooling": {
                "AWAY": cooling_away_temp,
                "VACATION": cooling_vacation_temp,
                "PARTY": cooling_party_temp,
            },
        }
        if thermostatunit_id or payload:
            pass
