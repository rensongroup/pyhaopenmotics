"""Module containing the base of an output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .models.groupaction import GroupAction

if TYPE_CHECKING:
    from ..client.openmoticscloud import (
        OpenMoticsCloud,  # pylint: disable=R0401
    )


@dataclass
class OpenMoticsGroupActions:
    """Object holding information of the OpenMotics groupactions.

    All actions related to groupaction or a specific groupaction.
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
        groupactions_filter: str | None = None,
    ) -> list[GroupAction]:
        """Call lists all GroupAction objects.

        Args:
        ----
            groupactions_filter: Optional filter

        Returns:
        -------
            Dict with all groupactions

        usage: The usage filter allows the GroupActions to be filtered for
            their intended usage.
            SCENE: These GroupActions can be considered a scene,
                e.g. watching tv or romantic dinner.
        # noqa: E800
        # [{
        #      "_version": <version>,
        #      "actions": [
        #          <action type>, <action number>,
        #          <action type>, <action number>,
        #          ...
        #      ],
        #  "id": <id>,
        #  "location": {
        #      "installation_id": <installation id>
        #  },
        #  "name": "<name>"
        #  }

        """
        path = f"/base/installations/{self._omcloud.installation_id}/groupactions"
        default_filter = '{"usage":"CONTROL"}'

        # Renson cloud uses by default usage=CONTROL filter
        # https://api.openmotics.com/api/v1.1/base/installations/1/groupsactions?filter={%22usage%22:%22CONTROL%22}
        query_params = {"filter": groupactions_filter} if groupactions_filter else {"filter": default_filter}

        body = await self._omcloud.get(
            path=path,
            params=query_params,
        )

        return [GroupAction.from_dict(groupaction) for groupaction in body["data"]]

    async def get_by_id(
        self,
        groupaction_id: int,
    ) -> GroupAction:
        """Get a specified groupaction object.

        Args:
        ----
            groupaction_id: int

        Returns:
        -------
            Returns a groupaction with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/groupactions/{groupaction_id}"

        body = await self._omcloud.get(path)

        return GroupAction.from_dict(body["data"])

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
        # E501 line too long
        path = f"/base/installations/{self._omcloud.installation_id}/groupactions/{groupaction_id}/trigger"
        return await self._omcloud.post(path)

    async def by_usage(
        self,
        groupaction_usage: str,
    ) -> Any:
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
        path = f"/base/installations/{self._omcloud.installation_id}/groupactions"
        query_params = {"usage": groupaction_usage.upper()}
        return await self._omcloud.get(path, params=query_params)

    async def scenes(self) -> Any:
        """Return all scenes object.

        SCENE: These GroupActions can be considered a scene,
            e.g. watching tv or romantic dinner.

        Returns
        -------
            Returns all scenes

        """
        return await self.by_usage("SCENE")
