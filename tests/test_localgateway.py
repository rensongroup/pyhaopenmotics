import ssl
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from pyhaopenmotics import (
    AuthenticationError,
    LocalGateway,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
)


@pytest.fixture
def localgateway():
    """Fixture for LocalGateway."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return LocalGateway("testuser", "testpass", "testlocalgw", session=session, verify_ssl=False)


@pytest.fixture
def localgateway_tls():
    """Fixture for LocalGateway with TLS enabled."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return LocalGateway(
        "testuser",
        "testpass",
        "testlocalgw",
        session=session,
        verify_ssl=True,
        ssl_context=ssl.create_default_context(),
    )


@pytest.mark.asyncio
async def test_localgateway_init(localgateway) -> None:
    """Test LocalGateway initialization."""
    assert localgateway.username == "testuser"
    assert localgateway.password == "testpass"
    assert localgateway.localgw == "testlocalgw"
    assert localgateway.request_timeout == 8
    assert localgateway.verify_ssl is False
    assert localgateway.auth == {"username": "testuser", "password": "testpass"}
    assert localgateway.session is not None
    assert localgateway.token is None
    assert localgateway.token_expires_at == 0
    assert "PyHAOpenMotics" in localgateway.user_agent
    assert isinstance(localgateway.ssl_context, ssl.SSLContext)

    localgateway_no_auth = LocalGateway(None, None, "testlocalgw", session=AsyncMock(), verify_ssl=False)
    assert localgateway_no_auth.auth is None


@pytest.mark.asyncio
async def test_localgateway_init_tls(localgateway_tls) -> None:
    """Test LocalGateway initialization with TLS."""
    assert localgateway_tls.verify_ssl is True
    assert localgateway_tls.ssl_context is not None
    assert isinstance(localgateway_tls.ssl_context, ssl.SSLContext)


@pytest.mark.asyncio
async def test_localgateway_request_success(localgateway) -> None:
    """Test LocalGateway _request method success."""
    # Mock the session.request method
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"success": True}
    mock_response.text.return_value = '{"success": true}'

    # Fix: Make session.request an AsyncMock that returns mock_response
    localgateway.session.request = AsyncMock(return_value=mock_response)

    result = await localgateway._request("/test", method="POST")

    assert result == {"success": True}
    localgateway.session.request.assert_called_once()
    # Check arguments
    args, kwargs = localgateway.session.request.call_args
    assert args[0] == "POST"
    assert "https://testlocalgw/test" in str(args[1])
    assert kwargs["ssl"] == localgateway.ssl_context


@pytest.mark.asyncio
async def test_localgateway_request_timeout(localgateway) -> None:
    """Test LocalGateway _request method timeout."""
    localgateway.session.request.side_effect = TimeoutError()

    with pytest.raises(OpenMoticsConnectionTimeoutError):
        await localgateway._request("/test")


@pytest.mark.asyncio
async def test_localgateway_request_connection_error(localgateway) -> None:
    """Test LocalGateway _request method connection error."""
    localgateway.session.request.side_effect = aiohttp.ClientError("error")

    with pytest.raises(OpenMoticsConnectionError):
        await localgateway._request("/test")


@pytest.mark.asyncio
async def test_localgateway_request_ssl_error(localgateway_tls) -> None:
    """Test LocalGateway _request method SSL error."""
    localgateway_tls.session.request.side_effect = aiohttp.ClientConnectorSSLError(None, os_error=OSError(1, "SSL Error"))

    with pytest.raises(OpenMoticsConnectionSslError):
        await localgateway_tls._request("/test")


@pytest.mark.asyncio
async def test_localgateway_request_authentication_error(localgateway) -> None:
    """Test LocalGateway _request method authentication error."""
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.headers = {}
    mock_response.raise_for_status = MagicMock()
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=(), status=401, message="Unauthorized", headers={}
    )
    localgateway.session.request = AsyncMock(return_value=mock_response)

    with pytest.raises(AuthenticationError):
        await localgateway._request("/test")


@pytest.mark.asyncio
async def test_localgateway_request_client_error(localgateway) -> None:
    """Test LocalGateway _request method client error."""
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.headers = {}
    mock_response.raise_for_status = MagicMock()
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=(), status=400, message="Bad Request", headers={}
    )
    localgateway.session.request = AsyncMock(return_value=mock_response)

    with pytest.raises(OpenMoticsConnectionError):
        await localgateway._request("/test")


@pytest.mark.asyncio
async def test_localgateway_exec_action(localgateway) -> None:
    """Test LocalGateway exec_action method."""
    localgateway.token = "fake_token"  # Set token to avoid get_token call
    localgateway.token_expires_at = 9999999999
    # We need to mock _request because it's called by exec_action which calls post
    localgateway._request = AsyncMock(return_value={"success": True})

    result = await localgateway.exec_action("/test", data={"key": "value"})

    assert result == {"success": True}
    localgateway._request.assert_called_once()
    assert localgateway._request.call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_localgateway_get_token_success(localgateway) -> None:
    """Test LocalGateway get_token method success."""
    localgateway._request = AsyncMock(return_value={"success": True, "token": "testtoken"})

    await localgateway.get_token()

    assert localgateway.token == "testtoken"
    assert localgateway.token_expires_at > 0
    localgateway._request.assert_called_once()
    assert localgateway._request.call_args.kwargs["data"] == localgateway.auth
    assert localgateway._request.call_args.kwargs["path"] == "login"


@pytest.mark.asyncio
async def test_localgateway_get_token_failure(localgateway) -> None:
    """Test LocalGateway get_token method failure."""
    localgateway._request = AsyncMock(return_value={"success": False})

    await localgateway.get_token()

    assert localgateway.token is None
    assert localgateway.token_expires_at == 0


@pytest.mark.asyncio
async def test_localgateway_get_auth_headers_no_token(localgateway) -> None:
    """Test LocalGateway _get_auth_headers method when no token."""
    # We need to mock get_token to verify it's called
    localgateway.get_token = AsyncMock()

    headers = await localgateway._get_auth_headers()

    assert "User-Agent" in headers
    assert "Accept" in headers
    localgateway.get_token.assert_called_once()


@pytest.mark.asyncio
async def test_localgateway_get_auth_headers_with_token(localgateway) -> None:
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
async def test_localgateway_get_auth_headers_expired_token(localgateway) -> None:
    """Test LocalGateway _get_auth_headers method when token is expired."""
    import time

    localgateway.get_token = AsyncMock()
    localgateway.token = "expired_token"
    # Set expiration to a time in the past
    localgateway.token_expires_at = time.time() - 100

    headers = await localgateway._get_auth_headers()

    assert "User-Agent" in headers
    assert "Accept" in headers
    localgateway.get_token.assert_called_once()


@pytest.mark.asyncio
async def test_localgateway_get_url(localgateway) -> None:
    """Test LocalGateway _get_url method."""
    url = await localgateway._get_url("/test")
    assert url == "https://testlocalgw/test"

    url_http = await localgateway._get_url("/test", scheme="http")
    # Port 443 is default for LocalGateway instance, so it appears in URL
    assert url_http == "http://testlocalgw:443/test"


@pytest.mark.asyncio
async def test_localgateway_get_auth_headers_with_headers_param(localgateway) -> None:
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
async def test_localgateway_properties(localgateway) -> None:
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
async def test_localgateway_close(localgateway) -> None:
    """Test LocalGateway close method."""
    localgateway._close_session = True
    session_mock = localgateway.session
    await localgateway.close()
    session_mock.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_localgateway_context_manager(localgateway) -> None:
    """Test LocalGateway context manager."""
    localgateway._close_session = True
    session_mock = localgateway.session
    async with localgateway as lgw:
        assert lgw is localgateway
        session_mock.close.assert_not_awaited()
    session_mock.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_localgateway_close_no_session(localgateway) -> None:
    """Test LocalGateway close method with no session."""
    localgateway.session = None
    await localgateway.close()
