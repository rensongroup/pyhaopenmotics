"""Module containing the base of an shutters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .models.shutter import Shutter

if TYPE_CHECKING:
    from ..client.localgateway import LocalGateway  # pylint: disable=R0401


@dataclass
class OpenMoticsShutters:
    """Object holding information of the OpenMotics shutters.

    All actions related to Shutters or a specific Shutter.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
        ----
            omcloud: LocalGateway

        """
        self._omcloud = omcloud
        self._shutter_configs: list[Any] = []

    @property
    def shutter_configs(self) -> list[Any]:
        """Get a list of all shutter confs.

        Returns
        -------
            list of all shutter confs

        """
        return self._shutter_configs

    @shutter_configs.setter
    def shutter_configs(self, shutter_configs: list[Any]) -> None:
        """Set a list of all shutter confs.

        Args:
        ----
            shutter_configs: list

        """
        self._shutter_configs = shutter_configs

    async def get_all(
        self,
        shutter_filter: str | None = None,
    ) -> list[Shutter]:
        """Get a list of all shutter objects.

        Args:
        ----
            shutter_filter: str

        Returns:
        -------
            list with all shutters

        """
        if len(self.shutter_configs) == 0:
            goc = await self._omcloud.exec_action("get_shutter_configurations")
            if goc["success"] is True:
                self.shutter_configs = goc["config"]

        shutters_status = await self._omcloud.exec_action("get_shutter_status")
        status = shutters_status["detail"]

        data = []
        for shutter in self.shutter_configs:
            shutter_id = str(shutter.get("id"))
            if shutter_id is not None and shutter_id in status:
                data.append(shutter | {"status": status[shutter_id]})
            else:
                data.append(shutter)

        shutters = [Shutter.from_dict(device) for device in data]

        if shutter_filter is not None:
            # implemented later
            pass

        return shutters  # pyright: ignore[reportReturnType]

    async def get_by_id(
        self,
        shutter_id: int,
    ) -> Shutter | None:
        """Get shutter by id.

        Args:
        ----
            shutter_id: int

        Returns:
        -------
            Returns a shutter with id

        """
        for shutter in await self.get_all():
            if shutter.idx == shutter_id:
                return shutter
        return None

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
        data = {"id": shutter_id}
        return await self._omcloud.exec_action("do_shutter_up", data=data)

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
        data = {"id": shutter_id}
        return await self._omcloud.exec_action("do_shutter_down", data=data)

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
        data = {"id": shutter_id}
        return await self._omcloud.exec_action("do_shutter_stop", data=data)

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
        data = {"id": shutter_id, "position": position}
        return await self._omcloud.exec_action("do_shutter_goto", data=data)
