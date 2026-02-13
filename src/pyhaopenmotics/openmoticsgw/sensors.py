"""Module containing the base of an sensor."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models.sensor import Sensor

if TYPE_CHECKING:
    from ..client.localgateway import LocalGateway  # pylint: disable=R0401


class OpenMoticsSensors:
    """Object holding information of the OpenMotics sensors.

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
    ) -> list[Sensor]:
        """Get a list of all sensor objects.

        Args:
        ----
            sensor_filter: str

        Returns:
        -------
            Dict with all sensors

        """
        if len(self.sensor_configs) == 0:
            goc = await self._omcloud.exec_action("get_sensor_configurations")
            if goc["success"] is True:
                self.sensor_configs = goc["config"]

        sensors_statuses = await self._omcloud.exec_action("get_sensor_status")
        statuses = {s["id"]: s for s in sensors_statuses["status"]}

        data = []
        for config in self.sensor_configs:
            sensor_config = config
            sensor_status = statuses.get(config["id"])
            if sensor_status:
                sensor_config["status"] = {
                    sensor_config.get("physical_quantity"): sensor_status.get("value"),
                }
            data.append(sensor_config)

        sensors = [Sensor.from_dict(device) for device in data]

        if sensor_filter is not None:
            # implemented later
            pass

        return sensors  # pyright: ignore[reportReturnType]

    async def get_by_id(
        self,
        sensor_id: int,
    ) -> Sensor | None:
        """Get sensor by id.

        Args:
        ----
            sensor_id: int

        Returns:
        -------
            Returns a sensor with id

        """
        for sensor in await self.get_all():
            if sensor.idx == sensor_id:
                return sensor
        return None
