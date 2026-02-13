"""Module containing the base of an sensor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client.openmoticscloud import (
        OpenMoticsCloud,  # pylint: disable=R0401
    )
    from .models.energy import EnergySensor

####################################################################################
#
# Energysensors don't exist in cloud api.
# This is implemented to keep on par with localgateway
#
###################################################################################


@dataclass
class OpenMoticsEnergySensors:
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
    ) -> list[EnergySensor]:
        """Get a list of all sensor objects.

        Args:
        ----
            sensor_filter: str

        Returns:
        -------
            Dict with all sensors

        """
        if sensor_filter:
            pass

        return []
