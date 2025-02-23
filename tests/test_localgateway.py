import asyncio

import aiohttp
import pytest
from aioresponses import aioresponses

from pyhaopenmotics.localgateway import (
    AuthenticationError,
    LocalGateway,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
)


@pytest.fixture
def local_gateway():
    return LocalGateway(
        username="test_user",
        password="test_pass",
        localgw="localhost",
        port=3000,
        tls=False,
    )


@pytest.mark.asyncio
async def test_get_token_success(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/login", payload={"success": True, "token": "test_token"})
        await local_gateway.get_token()
        assert local_gateway.token == "test_token"
        assert local_gateway.token_expires_at > 0


@pytest.mark.asyncio
async def test_get_token_failure(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/login", payload={"success": False})
        await local_gateway.get_token()
        assert local_gateway.token is None
        assert local_gateway.token_expires_at == 0


@pytest.mark.asyncio
async def test_request_timeout(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/test", exception=asyncio.TimeoutError)
        with pytest.raises(OpenMoticsConnectionTimeoutError):
            await local_gateway._request("test")


@pytest.mark.asyncio
async def test_request_ssl_error(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/test", exception=aiohttp.ClientConnectorSSLError)
        with pytest.raises(OpenMoticsConnectionSslError):
            await local_gateway._request("test")


@pytest.mark.asyncio
async def test_request_authentication_error(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/test", status=401)
        with pytest.raises(AuthenticationError):
            await local_gateway._request("test")


@pytest.mark.asyncio
async def test_request_connection_error(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/test", exception=aiohttp.ClientError)
        with pytest.raises(OpenMoticsConnectionError):
            await local_gateway._request("test")


@pytest.mark.asyncio
async def test_exec_action(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/test", payload={"result": "success"})
        response = await local_gateway.exec_action("test")
        assert response == {"result": "success"}


@pytest.mark.asyncio
async def test_subscribe_webhook(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/ws/events", payload={"result": "success"})
        await local_gateway.subscribe_webhook("installation_id")


@pytest.mark.asyncio
async def test_unsubscribe_webhook(local_gateway):
    with aioresponses() as m:
        m.delete("https://localhost:3000/ws/events", payload={"result": "success"})
        await local_gateway.unsubscribe_webhook()


@pytest.mark.asyncio
async def test_get_auth_headers_with_valid_token(local_gateway):
    local_gateway.token = "valid_token"
    local_gateway.token_expires_at = time.time() + 3600
    headers = await local_gateway._get_auth_headers()
    assert headers["Authorization"] == "Bearer valid_token"


@pytest.mark.asyncio
async def test_get_auth_headers_with_expired_token(local_gateway):
    local_gateway.token = "expired_token"
    local_gateway.token_expires_at = time.time() - 3600
    with aioresponses() as m:
        m.post("https://localhost:3000/login", payload={"success": True, "token": "new_token"})
        headers = await local_gateway._get_auth_headers()
    assert headers["Authorization"] == "Bearer new_token"


@pytest.mark.asyncio
async def test_close_session(local_gateway):
    await local_gateway.close()
    assert local_gateway.session is None


@pytest.mark.asyncio
async def test_aenter_aexit(local_gateway):
    async with local_gateway as lg:
        assert lg is local_gateway
    assert local_gateway.session is None


@pytest.mark.asyncio
async def test_request_with_custom_headers(local_gateway):
    custom_headers = {"Custom-Header": "CustomValue"}
    with aioresponses() as m:
        m.post("https://localhost:3000/test", payload={"result": "success"})
        response = await local_gateway._request("test", headers=custom_headers)
    assert response == {"result": "success"}


@pytest.mark.asyncio
async def test_request_with_data(local_gateway):
    data = {"key": "value"}
    with aioresponses() as m:
        m.post("https://localhost:3000/test", payload={"result": "success"})
        response = await local_gateway._request("test", data=data)
    assert response == {"result": "success"}


@pytest.mark.asyncio
async def test_request_with_invalid_json_response(local_gateway):
    with aioresponses() as m:
        m.post("https://localhost:3000/test", body="Invalid JSON", headers={"Content-Type": "application/json"})
        with pytest.raises(aiohttp.ContentTypeError):
            await local_gateway._request("test")
