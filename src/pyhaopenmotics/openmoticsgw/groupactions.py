"""Module containing the base of an groupaction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .models.groupaction import GroupAction

if TYPE_CHECKING:
    from ..client.localgateway import LocalGateway  # pylint: disable=R0401


@dataclass
class OpenMoticsGroupActions:
    """Object holding information of the OpenMotics groupactions.

    All actions related to groupaction or a specific groupaction.
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
        groupaction_filter: str | None = None,
    ) -> list[GroupAction]:
        """Call lists all GroupAction objects.

        Args:
        ----
            groupaction_filter: Optional filter

        Returns:
        -------
            list with all groupactions

        usage: The usage filter allows the GroupActions to be filtered for
            their intended usage.
            SCENE: These GroupActions can be considered a scene,
                e.g. watching tv or romantic dinner.

        """
        data = await self._omcloud.exec_action("get_group_action_configurations")

        if groupaction_filter is not None:
            # implemented later
            pass

        return [GroupAction.from_dict(device) for device in data["config"]]  # pyright: ignore[reportReturnType]

    async def get_by_id(
        self,
        groupaction_id: int,
    ) -> GroupAction | None:
        """Get a specified groupaction object.

        Args:
        ----
            groupaction_id: int

        Returns:
        -------
            Returns a groupaction with id

        """
        for groupaction in await self.get_all():
            if groupaction.idx == groupaction_id:
                return groupaction
        return None

    async def trigger(
        self,
        groupaction_id: int,
    ) -> Any:
        """Trigger a specified groupaction object.

        Args:
        ----
            groupaction_id: int

        Returns:
        -------
            Returns a groupaction with id

        """
        data = {"group_action_id": groupaction_id}
        return await self._omcloud.exec_action("do_group_action", data=data)

    async def by_usage(
        self,
        groupaction_usage: str,
    ) -> list[GroupAction]:
        """Return a specified groupaction object.

        The usage filter allows the GroupActions to be filtered for their
        intended usage.

        Args:
        ----
            groupaction_usage: str

        Returns:
        -------
            Returns a groupaction with id

        """
        return [groupaction for groupaction in await self.get_all() if groupaction.name == groupaction_usage]

    async def scenes(self) -> Any:
        """Return all scenes object.

        SCENE: These GroupActions can be considered a scene,
            e.g. watching tv or romantic dinner.

        Returns
        -------
            Returns all scenes

        """
        if (response := await self.by_usage("SCENE")) is None:
            return None
        return response
