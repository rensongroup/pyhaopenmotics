"""Module containing the base of an sensor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models.sensor import Sensor

if TYPE_CHECKING:
    from ..client.openmoticscloud import (
        OpenMoticsCloud,  # pylint: disable=R0401
    )


@dataclass
class OpenMoticsSensors:
    """Object holding information of the OpenMotics sensors.

    All actions related to Sensors or a specific Sensor.
    """

    def __init__(self, omcloud: OpenMoticsCloud) -> None:
        """Init the installations object.

        Args:
        ----
            omcloud: OpenMoticsCloud

        """
        self._omcloud = omcloud

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
        path = f"/base/installations/{self._omcloud.installation_id}/sensors"

        if sensor_filter:
            query_params = {"filter": sensor_filter}
            body = await self._omcloud.get(
                path=path,
                params=query_params,
            )
        else:
            body = await self._omcloud.get(path)

        return [Sensor.from_dict(sensor) for sensor in body["data"]]

    async def get_by_id(
        self,
        sensor_id: int,
    ) -> Sensor:
        """Get sensor by id.

        Args:
        ----
            sensor_id: int

        Returns:
        -------
            Returns a sensor with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/sensors/{sensor_id}"
        body = await self._omcloud.get(path)

        return Sensor.from_dict(body["data"])
