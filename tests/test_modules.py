from unittest.mock import AsyncMock

import pytest
from pyhaopenmotics import OpenMoticsCloud
from pyhaopenmotics.cloud.models.ventilation import VentilationUnit
from pyhaopenmotics.cloud.ventilations import OpenMoticsVentilationUnits


@pytest.fixture
def mock_cloud_client():
    client = AsyncMock(spec=OpenMoticsCloud)
    client.installation_id = 1
    return client


@pytest.mark.asyncio
async def test_ventilations_get_all(mock_cloud_client):
    ventilation_units = OpenMoticsVentilationUnits(mock_cloud_client)

    mock_data = {"data": [{"id": 1, "name": "Unit 1", "status": {"state": "ON", "mode": "AUTO"}, "local_id": 101}]}
    mock_cloud_client.get.return_value = mock_data

    units = await ventilation_units.get_all()

    assert len(units) == 1
    assert isinstance(units[0], VentilationUnit)
    assert units[0].idx == 1
    assert units[0].name == "Unit 1"
    assert units[0].status.state == "ON"
    mock_cloud_client.get.assert_called_with("/base/installations/1/ventilations/units")


@pytest.mark.asyncio
async def test_ventilations_get_by_id(mock_cloud_client):
    ventilation_units = OpenMoticsVentilationUnits(mock_cloud_client)

    mock_data = {"data": {"id": 1, "name": "Unit 1", "status": {"state": "ON", "mode": "AUTO"}, "local_id": 101}}
    mock_cloud_client.get.return_value = mock_data

    unit = await ventilation_units.get_by_id(1)

    assert isinstance(unit, VentilationUnit)
    assert unit.idx == 1
    assert unit.name == "Unit 1"
    assert unit.status.state == "ON"
    mock_cloud_client.get.assert_called_with("/base/installations/1/ventilations/units/1")


from pyhaopenmotics.cloud.energy import OpenMoticsEnergySensors


@pytest.mark.asyncio
async def test_energy_sensors_get_all(mock_cloud_client):
    energy_sensors = OpenMoticsEnergySensors(mock_cloud_client)
    sensors = await energy_sensors.get_all()
    assert sensors == []
