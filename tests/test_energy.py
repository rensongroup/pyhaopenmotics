"""Tests for the local gateway energy sensors."""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from pyhaopenmotics import LocalGateway
from pyhaopenmotics.openmoticsgw.energy import OpenMoticsEnergySensors

INPUTS_PER_MODULE = 8
REALTIME_POWER = [230.0, 50.0, 1.0, 230.0]
REALTIME_POWER_MODULE_3 = [231.0, 50.0, 2.0, 462.0]


def _power_module(module_id: int) -> dict[str, Any]:
    """Build a `get_power_modules` entry for a power module."""
    module: dict[str, Any] = {"id": module_id}
    for idx in range(INPUTS_PER_MODULE):
        module[f"input{idx}"] = f"Module {module_id} input {idx}"
        module[f"inverted{idx}"] = False
    return module


@pytest.mark.asyncio
async def test_get_all_skips_module_missing_from_realtime_power() -> None:
    """A module missing from `get_realtime_power` is skipped without shifting later ids."""
    gateway = AsyncMock(spec=LocalGateway)
    gateway.exec_action.side_effect = [
        {"success": True, "modules": [_power_module(1), _power_module(2), _power_module(3)]},
        {
            "success": True,
            "1": [REALTIME_POWER] * INPUTS_PER_MODULE,
            "3": [REALTIME_POWER_MODULE_3] * INPUTS_PER_MODULE,
        },
    ]

    sensors = await OpenMoticsEnergySensors(gateway).get_all()

    assert [sensor.idx for sensor in sensors] == list(range(8)) + list(range(16, 24))
    module_3_first = sensors[INPUTS_PER_MODULE]
    assert module_3_first.name == "Module 3 input 0"
    assert module_3_first.status is not None
    assert module_3_first.status.power == REALTIME_POWER_MODULE_3[3]


@pytest.mark.asyncio
async def test_get_all_with_all_modules_present() -> None:
    """Ids stay contiguous when every module reports realtime power."""
    gateway = AsyncMock(spec=LocalGateway)
    gateway.exec_action.side_effect = [
        {"success": True, "modules": [_power_module(1), _power_module(2)]},
        {
            "success": True,
            "1": [REALTIME_POWER] * INPUTS_PER_MODULE,
            "2": [REALTIME_POWER] * INPUTS_PER_MODULE,
        },
    ]

    sensors = await OpenMoticsEnergySensors(gateway).get_all()

    assert [sensor.idx for sensor in sensors] == list(range(2 * INPUTS_PER_MODULE))
