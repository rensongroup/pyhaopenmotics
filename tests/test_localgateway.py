import ssl
from unittest.mock import AsyncMock

import aiohttp
import pytest

from pyhaopenmotics import (
    AuthenticationError,
    LocalGateway,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
)
from pyhaopenmotics.errors import OpenMoticsConnectionSslError


@pytest.fixture
def localgateway():
    """Fixture for LocalGateway."""
    return LocalGateway("testuser", "testpass", "testlocalgw", session=AsyncMock(), tls=False)


@pytest.fixture
def localgateway_tls():
    """Fixture for LocalGateway with TLS enabled."""
    return LocalGateway(
        "testuser",
        "testpass",
        "testlocalgw",
        session=AsyncMock(),
        tls=True,
        ssl_context=ssl.create_default_context(),
    )


@pytest.mark.asyncio
async def test_localgateway_init(localgateway):
    """Test LocalGateway initialization."""
    assert localgateway.username == "testuser"
    assert localgateway.password == "testpass"
    assert localgateway.localgw == "testlocalgw"
    assert localgateway.request_timeout == 8
    assert localgateway.tls is False
    assert localgateway.auth == {"username": "testuser", "password": "testpass"}
    assert localgateway.session is not None
    assert localgateway.token is None
    assert localgateway.token_expires_at == 0
    assert "PyHAOpenMotics" in localgateway.user_agent
    assert isinstance(localgateway.ssl_context, ssl.SSLContext)

    localgateway_no_auth = LocalGateway(None, None, "testlocalgw", session=AsyncMock(), tls=False)
    assert localgateway_no_auth.auth is None


@pytest.mark.asyncio
async def test_localgateway_init_tls(localgateway_tls):
    """Test LocalGateway initialization with TLS."""
    assert localgateway_tls.tls is True
    assert localgateway_tls.ssl_context is not None
    assert isinstance(localgateway_tls.ssl_context, ssl.SSLContext)


@pytest.mark.asyncio
async def test_localgateway_request_success(localgateway):
    """Test LocalGateway _request method success."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"success": True}
    localgateway.session.request.return_value.__aenter__.return_value = mock_response

    result = await localgateway._request("/test", method="POST")

    assert result == {"success": True}
    localgateway.session.request.assert_called_once()
    assert "https://testlocalgw:443/test" in str(localgateway.session.request.call_args.args[1])
    assert localgateway.session.request.call_args.kwargs["ssl"] == localgateway.ssl_context


@pytest.mark.asyncio
async def test_localgateway_request_timeout(localgateway):
    """Test LocalGateway _request method timeout."""
    localgateway.session.request.side_effect = TimeoutError()

    with pytest.raises(OpenMoticsConnectionTimeoutError):
        await localgateway._request("/test")


@pytest.mark.asyncio
async def test_localgateway_request_connection_error(localgateway):
    """Test LocalGateway _request method connection error."""
    localgateway.session.request.side_effect = aiohttp.ClientError()

    with pytest.raises(OpenMoticsConnectionError):
        await localgateway._request("/test")


@pytest.mark.asyncio
async def test_localgateway_request_ssl_error(localgateway_tls):
    """Test LocalGateway _request method SSL error."""
    localgateway_tls.session.request.side_effect = aiohttp.ClientConnectorSSLError(None, None)

    with pytest.raises(OpenMoticsConnectionSslError):
        await localgateway_tls._request("/test")


@pytest.mark.asyncio
async def test_localgateway_request_authentication_error(localgateway):
    """Test LocalGateway _request method authentication error."""
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(None, ())
    localgateway.session.request.return_value.__aenter__.return_value = mock_response

    with pytest.raises(AuthenticationError):
        await localgateway._request("/test")


@pytest.mark.asyncio
async def test_localgateway_request_client_error(localgateway):
    """Test LocalGateway _request method client error."""
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(None, ())
    localgateway.session.request.return_value.__aenter__.return_value = mock_response
    with pytest.raises(OpenMoticsConnectionError):
        await localgateway._request("/test")


@pytest.mark.asyncio
async def test_localgateway_exec_action(localgateway):
    """Test LocalGateway exec_action method."""
    localgateway._request = AsyncMock(return_value={"success": True})

    result = await localgateway.exec_action("/test", data={"key": "value"})

    assert result == {"success": True}
    localgateway._request.assert_called_once()
    assert localgateway._request.call_args.kwargs["method"] == aiohttp.hdrs.METH_POST


@pytest.mark.asyncio
async def test_localgateway_get_token_success(localgateway):
    """Test LocalGateway get_token method success."""
    localgateway._request = AsyncMock(return_value={"success": True, "token": "testtoken"})

    await localgateway.get_token()

    assert localgateway.token == "testtoken"
    assert localgateway.token_expires_at > 0
    localgateway._request.assert_called_once()
    assert localgateway._request.call_args.kwargs["data"] == localgateway.auth
    assert localgateway._request.call_args.kwargs["path"] == "login"


@pytest.mark.asyncio
async def test_localgateway_get_token_failure(localgateway):
    """Test LocalGateway get_token method failure."""
    localgateway._request = AsyncMock(return_value={"success": False})

    await localgateway.get_token()

    assert localgateway.token is None
    assert localgateway.token_expires_at == 0


@pytest.mark.asyncio
async def test_localgateway_subscribe_webhook(localgateway):
    """Test LocalGateway subscribe_webhook method."""
    localgateway._request = AsyncMock()
    localgateway._get_auth_headers = AsyncMock(return_value={})
    await localgateway.subscribe_webhook(1)

    localgateway._request.assert_called_once()
    assert localgateway._request.call_args.kwargs["data"] == {
        "action": "set_subscription",
        "types": [
            "OUTPUT_CHANGE",
            "SHUTTER_CHANGE",
            "THERMOSTAT_CHANGE",
            "THERMOSTAT_GROUP_CHANGE",
        ],
        "installation_ids": [1],
    }
    assert localgateway._request.call_args.kwargs["method"] == aiohttp.hdrs.METH_POST


@pytest.mark.asyncio
async def test_localgateway_unsubscribe_webhook(localgateway):
    """Test LocalGateway unsubscribe_webhook method."""
    localgateway._request = AsyncMock()
    localgateway._get_auth_headers = AsyncMock(return_value={})
    await localgateway.unsubscribe_webhook()

    localgateway._request.assert_called_once()
    assert localgateway._request.call_args.kwargs["method"] == aiohttp.hdrs.METH_DELETE


@pytest.mark.asyncio
async def test_localgateway_get_auth_headers_no_token(localgateway):
    """Test LocalGateway _get_auth_headers method when no token."""
    localgateway.get_token = AsyncMock()
    headers = await localgateway._get_auth_headers()

    assert "User-Agent" in headers
    assert "Accept" in headers
    assert "Authorization" in headers
    localgateway.get_token.assert_called_once()


@pytest.mark.asyncio
async def test_localgateway_get_auth_headers_with_token(localgateway):
    """Test LocalGateway _get_auth_headers method with token."""
    localgateway.get_token = AsyncMock()
    localgateway.token = "testtoken"
    localgateway.token_expires_at = 9999999999

    headers = await localgateway._get_auth_headers()

    assert "User-Agent" in headers
    assert "Accept" in headers
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer testtoken"
    localgateway.get_token.assert_not_called()


@pytest.mark.asyncio
async def test_localgateway_get_auth_headers_with_headers_param(localgateway):
    """Test LocalGateway _get_auth_headers method with headers param."""
    localgateway.get_token = AsyncMock()
    localgateway.token = "testtoken"
    localgateway.token_expires_at = 9999999999
    headers = await localgateway._get_auth_headers({"test": "header"})

    assert "test" in headers
    assert headers["test"] == "header"
    assert "User-Agent" in headers
    assert "Accept" in headers
    assert "Authorization" in headers
    localgateway.get_token.assert_not_called()


@pytest.mark.asyncio
async def test_localgateway_properties(localgateway):
    """Test LocalGateway properties."""
    assert localgateway.inputs is not None
    assert localgateway.outputs is not None
    assert localgateway.groupactions is not None
    assert localgateway.lights is not None
    assert localgateway.sensors is not None
    assert localgateway.energysensors is not None
    assert localgateway.shutters is not None
    assert localgateway.thermostats is not None


@pytest.mark.asyncio
async def test_localgateway_close(localgateway):
    """Test LocalGateway close method."""
    await localgateway.close()
    localgateway.session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_localgateway_context_manager(localgateway):
    """Test LocalGateway context manager."""
    async with localgateway as lgw:
        assert lgw is localgateway
        localgateway.session.close.assert_not_awaited()
    localgateway.session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_localgateway_close_no_session(localgateway):
    """Test LocalGateway close method with no session."""
    localgateway.session = None
    await localgateway.close()
