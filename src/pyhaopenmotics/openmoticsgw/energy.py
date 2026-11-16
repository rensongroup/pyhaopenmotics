"""Module containing the base of an energy sensor."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .models.energy import EnergySensor

if TYPE_CHECKING:
    from ..client.localgateway import LocalGateway

_LOGGER = logging.getLogger(__name__)


class OpenMoticsEnergySensors:
    """Object holding information of the OpenMotics energy sensors.

    All actions related to Sensors or a specific Sensor.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
        ----
            omcloud: LocalGateway

        """
        self._omcloud = omcloud
        self._sensor_configs: list[Any] = []

    @property
    def sensor_configs(self) -> list[Any]:
        """Get a list of all sensor confs.

        Returns
        -------
            list of all sensor confs

        """
        return self._sensor_configs

    @sensor_configs.setter
    def sensor_configs(self, sensor_configs: list[Any]) -> None:
        """Set a list of all sensor confs.

        Args:
        ----
            sensor_configs: list

        """
        self._sensor_configs = sensor_configs

    async def get_all(
        self,
        sensor_filter: str | None = None,
    ) -> list[EnergySensor]:
        """Get a list of all energy sensor objects.

        Args:
        ----
            sensor_filter: str

        Returns:
        -------
            List with all energy sensors

        """
        if len(self.sensor_configs) == 0:
            goc = await self._omcloud.exec_action("get_power_modules")
            if goc["success"] is True:
                self.sensor_configs = goc["modules"]

        sensors_status = await self._omcloud.exec_action("get_realtime_power") or {}

        data = []
        total_idx = 0
        for module in self.sensor_configs:
            if module.get("id") is None:
                continue
            module_id = str(module["id"])
            statuses = sensors_status.get(module_id)
            if statuses is None:
                # The gateway omits a module from `get_realtime_power` when reading it fails
                # (communication timeout, maintenance mode, ...). Keep a placeholder without status
                # for each input, so the list positions and ids of all sensors stay stable.
                _LOGGER.debug("No realtime power data for energy module %s", module_id)
                statuses = [None] * self._number_of_inputs(module)
            for idx, status in enumerate(statuses):
                data.append(
                    {
                        "id": total_idx,
                        "name": module[f"input{idx}"],
                        "inverted": module[f"inverted{idx}"],
                        "status": status,
                    },
                )
                total_idx += 1

        if sensor_filter is not None:
            # implemented later
            pass

        return [EnergySensor.from_dict(device) for device in data]  # pyright: ignore[reportReturnType]

    @staticmethod
    def _number_of_inputs(module: dict[str, Any]) -> int:
        """Return the number of inputs defined in an energy module configuration."""
        return sum(1 for key in module if key.startswith("input") and key.removeprefix("input").isdigit())

    async def get_by_id(
        self,
        sensor_id: int,
    ) -> EnergySensor | None:
        """Get energy sensor by id.

        Args:
        ----
            sensor_id: int

        Returns:
        -------
            Returns an energy sensor with id

        """
        for sensor in await self.get_all():
            if sensor.idx == sensor_id:
                return sensor
        return None
