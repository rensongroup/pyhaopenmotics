"""Module containing the base of an output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models.input import OMInput

if TYPE_CHECKING:
    from ..client.openmoticscloud import (
        OpenMoticsCloud,  # pylint: disable=R0401
    )


@dataclass
class OpenMoticsInputs:
    """Object holding information of the OpenMotics inputs.

    All actions related to Inputs or a specific Input.
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
        input_filter: str | None = None,
    ) -> list[OMInput]:
        """Get a list of all input objects.

        Args:
        ----
            input_filter: str

        Returns:
        -------
            A list of inputs

        """
        path = f"/base/installations/{self._omcloud.installation_id}/inputs"

        if input_filter:
            query_params = {"filter": input_filter}
            body = await self._omcloud.get(
                path=path,
                params=query_params,
            )
        else:
            body = await self._omcloud.get(path)

        return [OMInput.from_dict(ominput) for ominput in body["data"]]

    async def get_by_id(
        self,
        input_id: int,
    ) -> OMInput:
        """Get input by id.

        Args:
        ----
            input_id: int

        Returns:
        -------
            Returns a input with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/inputs/{input_id}"
        body = await self._omcloud.get(path)

        return OMInput.from_dict(body["data"])
