"""Module containing the base of an light."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .models.light import Light

if TYPE_CHECKING:
    from ..client.openmoticscloud import (
        OpenMoticsCloud,  # pylint: disable=R0401
    )


@dataclass
class OpenMoticsLights:
    """Object holding information of the OpenMotics lights.

    All actions related to lights or a specific light.
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
        light_filter: str | None = None,
    ) -> list[Light]:
        """Get a list of all light objects.

        Args:
        ----
            light_filter: str

        Returns:
        -------
            Dict with all lights

        """
        path = f"/base/installations/{self._omcloud.installation_id}/lights"

        if light_filter:
            query_params = {"filter": light_filter}
            body = await self._omcloud.get(
                path=path,
                params=query_params,
            )
        else:
            body = await self._omcloud.get(path)

        return [Light.from_dict(light) for light in body["data"]]

    async def get_by_id(
        self,
        light_id: int,
    ) -> Light:
        """Get light by id.

        Args:
        ----
            light_id: int

        Returns:
        -------
            Returns a light with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/lights/{light_id}"
        body = await self._omcloud.get(path)

        return Light.from_dict(body["data"])

    async def toggle(
        self,
        light_id: int,
    ) -> Any:
        """Toggle a specified light object.

        Args:
        ----
            light_id: int

        Returns:
        -------
            Returns a light with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/lights/{light_id}/toggle"
        return await self._omcloud.post(path)

    async def turn_on(
        self,
        light_id: int,
        value: int | None = None,
    ) -> Any:
        """Turn on a specified light object.

        Args:
        ----
            light_id: int
            value: <0 - 100>

        Returns:
        -------
            Returns a light with id

        """
        payload = {}

        if value is not None:
            value = min(value, 100)
            value = max(0, value)
            payload = {"value": value}

        path = f"/base/installations/{self._omcloud.installation_id}/lights/{light_id}/turn_on"
        return await self._omcloud.post(path, json=payload)

    async def turn_off(
        self,
        light_id: int | None = None,
    ) -> Any:
        """Turn off a specified light object.

        Args:
        ----
            light_id: int

        Returns:
        -------
            Returns a light with id

        """
        if light_id is None:
            # Turn off all lights
            path = f"/base/installations/{self._omcloud.installation_id}/lights/turn_off"
        else:
            # Turn off light with id
            path = f"/base/installations/{self._omcloud.installation_id}/lights/{light_id}/turn_off"
        return await self._omcloud.post(path)
