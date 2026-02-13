"""Module containing the base of an ventilation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models.ventilation import VentilationUnit

if TYPE_CHECKING:
    from ..client.openmoticscloud import (
        OpenMoticsCloud,  # pylint: disable=R0401
    )


@dataclass
class OpenMoticsVentilationUnits:
    """Object holding information of the OpenMotics ventilations.

    All actions related to ventilations or a specific ventilation.
    """

    def __init__(self, _omcloud: OpenMoticsCloud) -> None:
        """Init the installations object.

        Args:
        ----
            _omcloud: _omcloud

        """
        self._omcloud = _omcloud

    async def get_all(
        self,
    ) -> list[VentilationUnit]:
        """Get a list of all ventilationunit objects.

        Args:
        ----
            None:

        Returns:
        -------
            Dict with all ventilationunits

        """
        path = f"/base/installations/{self._omcloud.installation_id}/ventilations/units"

        body = await self._omcloud.get(path)

        return [VentilationUnit.from_dict(ventilationunit) for ventilationunit in body["data"]]

    async def get_by_id(
        self,
        ventilationunit_id: int,
    ) -> VentilationUnit:
        """Get ventilationgroup_id by id.

        Args:
        ----
            ventilationunit_id: int

        Returns:
        -------
            Returns a ventilationunit with id

        """
        path = f"/base/installations/{self._omcloud.installation_id}/ventilations/units/{ventilationunit_id}"
        body = await self._omcloud.get(path)

        return VentilationUnit.from_dict(body["data"])
