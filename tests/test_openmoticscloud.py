import asyncio

import aiohttp
import pytest
from aioresponses import aioresponses

from pyhaopenmotics.errors import OpenMoticsConnectionError, OpenMoticsConnectionTimeoutError
from pyhaopenmotics.openmoticscloud import OpenMoticsCloud


@pytest.fixture
async def openmotics_cloud():
    async with aiohttp.ClientSession() as session:
        yield OpenMoticsCloud(token="test_token", session=session)


@pytest.mark.asyncio
async def test_get_request(openmotics_cloud):
    with aioresponses() as m:
        m.get("https://api.openmotics.com/test", payload={"key": "value"})

        response = await openmotics_cloud.get("/test")
        assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_post_request(openmotics_cloud):
    with aioresponses() as m:
        m.post("https://api.openmotics.com/test", payload={"key": "value"})

        response = await openmotics_cloud.post("/test", json={"data": "test"})
        assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_request_timeout(openmotics_cloud):
    with aioresponses() as m:
        m.get("https://api.openmotics.com/test", exception=asyncio.TimeoutError)

        with pytest.raises(OpenMoticsConnectionTimeoutError):
            await openmotics_cloud.get("/test")


@pytest.mark.asyncio
async def test_request_connection_error(openmotics_cloud):
    with aioresponses() as m:
        m.get("https://api.openmotics.com/test", exception=aiohttp.ClientError)

        with pytest.raises(OpenMoticsConnectionError):
            await openmotics_cloud.get("/test")


@pytest.mark.asyncio
async def test_subscribe_webhook(openmotics_cloud):
    with aioresponses() as m:
        m.post("https://api.openmotics.com/ws/events", status=200)

        await openmotics_cloud.subscribe_webhook()


@pytest.mark.asyncio
async def test_unsubscribe_webhook(openmotics_cloud):
    with aioresponses() as m:
        m.delete("https://api.openmotics.com/ws/events", status=200)

        await openmotics_cloud.unsubscribe_webhook()


@pytest.mark.asyncio
async def test_invalid_token():
    async with aiohttp.ClientSession() as session:
        with pytest.raises(ValueError):
            OpenMoticsCloud(token=None, session=session)


@pytest.mark.asyncio
async def test_invalid_url(openmotics_cloud):
    with aioresponses() as m:
        m.get("https://invalid.url/test", exception=aiohttp.ClientError)

        with pytest.raises(OpenMoticsConnectionError):
            await openmotics_cloud.get("https://invalid.url/test")


@pytest.mark.asyncio
async def test_get_request_with_params(openmotics_cloud):
    with aioresponses() as m:
        m.get("https://api.openmotics.com/test?param=value", payload={"key": "value"})

        response = await openmotics_cloud.get("/test", params={"param": "value"})
        assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_post_request_with_data(openmotics_cloud):
    with aioresponses() as m:
        m.post("https://api.openmotics.com/test", payload={"key": "value"})

        response = await openmotics_cloud.post("/test", data={"data": "test"})
        assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_request_with_invalid_json(openmotics_cloud):
    with aioresponses() as m:
        m.get("https://api.openmotics.com/test", body="Invalid JSON", status=200)

        response = await openmotics_cloud.get("/test")
        assert response == "Invalid JSON"


@pytest.mark.asyncio
async def test_request_with_404_error(openmotics_cloud):
    with aioresponses() as m:
        m.get("https://api.openmotics.com/test", status=404)

        with pytest.raises(OpenMoticsConnectionError):
            await openmotics_cloud.get("/test")


@pytest.mark.asyncio
async def test_request_with_500_error(openmotics_cloud):
    with aioresponses() as m:
        m.get("https://api.openmotics.com/test", status=500)

        with pytest.raises(OpenMoticsConnectionError):
            await openmotics_cloud.get("/test")


@pytest.mark.asyncio
async def test_close_session(openmotics_cloud):
    await openmotics_cloud.close()
    assert openmotics_cloud.session.closed


@pytest.mark.asyncio
async def test_installation_id_property(openmotics_cloud):
    openmotics_cloud.installation_id = 123
    assert openmotics_cloud.installation_id == 123


@pytest.mark.asyncio
async def test_user_agent(openmotics_cloud):
    assert openmotics_cloud.user_agent.startswith("PyHAOpenMotics/")
