"""Module containing the base of an output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..helpers import merge_dicts
from .models.output import Output

if TYPE_CHECKING:
    from ..client.localgateway import LocalGateway  # pylint: disable=R0401


@dataclass
class OpenMoticsOutputs:
    """Object holding information of the OpenMotics outputs.

    All actions related to Outputs or a specific Output.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
        ----
            omcloud: LocalGateway

        """
        self._omcloud = omcloud
        self._output_configs: list[Any] = []

    @property
    def output_configs(self) -> list[Any]:
        """Get a list of all output confs.

        Returns
        -------
            list of all output confs

        """
        return self._output_configs

    @output_configs.setter
    def output_configs(self, output_configs: list[Any]) -> None:
        """Set a list of all output confs.

        Args:
        ----
            output_configs: list

        """
        self._output_configs = output_configs

    async def get_all(
        self,
        output_filter: str | None = None,
    ) -> list[Output]:
        """Get a list of all output objects.

        Args:
        ----
            output_filter: str

        Returns:
        -------
            list with all outputs

        """
        if len(self.output_configs) == 0:
            goc = await self._omcloud.exec_action("get_output_configurations")
            if goc["success"] is True:
                self.output_configs = goc["config"]

        outputs_status = await self._omcloud.exec_action("get_output_status")
        status = outputs_status["status"]

        data = merge_dicts(self.output_configs, "status", status)

        if output_filter is not None:
            # implemented later
            pass

        return [Output.from_dict(device) for device in data]  # pyright: ignore[reportReturnType]

    async def get_by_id(
        self,
        output_id: int,
    ) -> Output | None:
        """Get output by id.

        Args:
        ----
            output_id: int

        Returns:
        -------
            Returns a output with id

        """
        for output in await self.get_all():
            if output.idx == output_id:
                return output
        return None

    async def toggle(
        self,
        output_id: int,
    ) -> Any:
        """Toggle a specified Output object.

        Args:
        ----
            output_id: int

        Returns:
        -------
            Returns a output with id

        """
        if (output := await self.get_by_id(output_id)) is None:
            return None
        try:
            if output.status.on is True:  # pyright: ignore[reportOptionalMemberAccess]
                return await self.turn_off(output_id)
            return await self.turn_on(output_id)
        except AttributeError, KeyError:
            return None

    async def turn_on(
        self,
        output_id: int,
        value: int | None = None,
    ) -> Any:
        """Turn on a specified Output object.

        Args:
        ----
            output_id: int
            value: <0 - 100>

        Returns:
        -------
            Returns a output with id

        """
        if value is not None:
            # value: <0 - 100>
            value = min(value, 100)
            value = max(0, value)

        data = {"id": output_id, "is_on": True}
        if value is not None:
            data["dimmer"] = value
        return await self._omcloud.exec_action("set_output", data=data)

    async def turn_off(
        self,
        output_id: int,
    ) -> Any:
        """Turn off a specified Output object.

        Args:
        ----
            output_id: int

        Returns:
        -------
            Returns a output with id

        """
        data = {"id": output_id, "is_on": False}
        return await self._omcloud.exec_action("set_output", data=data)
