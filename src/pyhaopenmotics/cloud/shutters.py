"""Module containing the base of an output."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .models.shutter import Shutter

if TYPE_CHECKING:
    from ..client.openmoticscloud import (
        OpenMoticsCloud,  # pylint: disable=R0401
    )


@dataclass
class OpenMoticsShutters:
    """Object holding information of the OpenMotics shutters.

    All actions related to Shutters or a specific Shutter.
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
        shutter_filter: str | None = None,
    ) -> list[Shutter]:
        """List all Shutter objects.

        Args:
        ----
            shutter_filter: Optional filter

        Returns:
        -------
            Dict with all shutters

        usage: The usage filter allows the Shutters to be filtered for their
            intended usage.
            CONTROL: These Shutters can be controlled directly and are not
                managed by an internal process.

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters"
        default_filter = '{"usage":"CONTROL"}'

        # Renson cloud uses by default usage=CONTROL filter
        # https://api.openmotics.com/api/v1.1/base/installations/1/shutters?filter={%22usage%22:%22CONTROL%22}
        query_params = {"filter": shutter_filter} if shutter_filter else {"filter": default_filter}

        body = await self._omcloud.get(
            path=path,
            params=query_params,
        )

        return [Shutter.from_dict(shutter) for shutter in body["data"]]

    async def get_by_id(
        self,
        shutter_id: int,
    ) -> Shutter:
        """Get a specified Shutter object.

        Args:
        ----
            shutter_id: int

        Returns:
        -------
            Returns a shutter with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}"
        body = await self._omcloud.get(path)

        return Shutter.from_dict(body["data"])

    async def move_up(
        self,
        shutter_id: int,
    ) -> Any:
        """Move the specified Shutter into the upwards position.

        Args:
        ----
            shutter_id: int

        Returns:
        -------
            Returns a shutter with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/open"
        return await self._omcloud.post(path)

    async def move_down(
        self,
        shutter_id: int,
    ) -> Any:
        """Move the specified Shutter into the downwards position.

        Args:
        ----
            shutter_id: int

        Returns:
        -------
            Returns a shutter with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/close"
        return await self._omcloud.post(path)

    async def stop(
        self,
        shutter_id: int,
    ) -> Any:
        """Stop any movement of the specified Shutter.

        Args:
        ----
            shutter_id: int

        Returns:
        -------
            Returns a shutter with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/stop"
        return await self._omcloud.post(path)

    async def change_position(
        self,
        shutter_id: int,
        position: int,
    ) -> Any:
        """Change the position of the specified Shutter.

        The position can be set from 0 to steps (excluded). The steps value can be
        found in the configuration field of a Shutter.
        Not all gateways or shutters support this feature.

        Args:
        ----
            shutter_id: int
            position: int  (in body)

        Returns:
        -------
            Returns a shutter with id

        """
        # E501 line too long
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/change_position"
        payload = json.dumps(
            {
                "position": position,
            },
        )
        return await self._omcloud.post(path, json=payload)

    async def change_relative_position(
        self,
        shutter_id: int,
        offset: int,
    ) -> Any:
        """Change the relative position of the specified Shutter.

        The offset can be set from -steps (excluded) to steps (excluded).
        The steps value can be found in the configuration field of a Shutter.
        Not all gateways or shutters support this feature.

        Args:
        ----
            shutter_id: int
            offset: int (in body)

        Returns:
        -------
            Returns a shutter with id

        """
        # E501 line too long
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/change_relative_position"
        payload = json.dumps(
            {
                "offset": offset,
            },
        )
        return await self._omcloud.post(path, json=payload)

    async def lock(
        self,
        shutter_id: int,
    ) -> Any:
        """Lock the specified Shutter to prevent future movements.

        The behavior is depending of the capabilities of the Shutter:
            LOCAL_LOCK capability: this lock is a hardware lock, without manual
            override through a local interface.
            CLOUD_LOCK capability: this lock is a software lock in the cloud,
            thus you can still move the shutter through a local interface.


        Args:
        ----
            shutter_id: int

        Returns:
        -------
            Returns the lock_type as response.

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/lock"
        return await self._omcloud.post(path)

    async def unlock(
        self,
        shutter_id: int,
    ) -> Any:
        """Undo the lock action of the specified Shutter.

        Args:
        ----
            shutter_id: int

        Returns:
        -------
            Returns a shutter with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/unlock"
        return await self._omcloud.post(path)

    async def preset(
        self,
        shutter_id: int,
        position: int,
    ) -> Any:
        """Change the preset position of the specified Shutter.

        The position can be set from 0 to steps (excluded). The steps value can be
        found in the configuration field of a Shutter.
        Not all gateways or shutters support this feature.

        Args:
        ----
            shutter_id: int
            position: int (in body)

        Returns:
        -------
            Returns a shutter with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/preset"
        payload = json.dumps(
            {
                "position": position,
            },
        )
        return await self._omcloud.post(path, json=payload)

    async def move_to_preset(
        self,
        shutter_id: int,
    ) -> Any:
        """Move the specified Shutter to its preset position (defined in POST .../preset).

        Not all gateways or shutters support this feature.

        Args:
        ----
            shutter_id: int

        Returns:
        -------
            Returns a shutter with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/shutters/{shutter_id}/move"
        return await self._omcloud.post(path)
