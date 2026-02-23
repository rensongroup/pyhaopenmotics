"""Module containing the base of an light."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client.localgateway import LocalGateway  # pylint: disable=R0401
    from .models.light import Light


@dataclass
class OpenMoticsLights:
    """Object holding information of the OpenMotics lights.

    All actions related to lights or a specific light.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
        ----
            omcloud: LocalGateway

        """
        self._omcloud = omcloud

    async def get_all(
        self,
        light_filter: str | None = None,  # pylint: disable=unused-argument
    ) -> list[Light]:
        """Get a list of all light objects.

        Args:
        ----
            light_filter: str

        Returns:
        -------
            list with all lights

        """
        if light_filter is not None:
            # implemented later
            pass

        return []
