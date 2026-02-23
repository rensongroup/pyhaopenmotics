"""Module containing the base of an energy sensor."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models.energy import EnergySensor

if TYPE_CHECKING:
    from ..client.localgateway import LocalGateway


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

        sensors_status = await self._omcloud.exec_action("get_realtime_power")

        data = []
        total_idx = 0
        for module in self.sensor_configs:
            module_id = str(module.get("id"))
            if module_id is None:
                continue
            for idx, status in enumerate(sensors_status[module_id]):
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
