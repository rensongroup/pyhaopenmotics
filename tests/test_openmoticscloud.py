from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from pyhaopenmotics import OpenMoticsCloud, OpenMoticsConnectionError, OpenMoticsConnectionTimeoutError


@pytest.fixture
def openmotics_cloud():
    session = AsyncMock(spec=aiohttp.ClientSession)
    return OpenMoticsCloud(token="test_token", session=session)


@pytest.mark.asyncio
async def test_get_request(openmotics_cloud) -> None:
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"key": "value"}

    openmotics_cloud.session.request = AsyncMock(return_value=mock_response)

    response = await openmotics_cloud.get("/test")
    assert response == {"key": "value"}

    # Check if request was called correctly
    args, _kwargs = openmotics_cloud.session.request.call_args
    assert args[0] == "GET"
    assert str(args[1]) == "https://api.openmotics.com/api/v1.1/test"


@pytest.mark.asyncio
async def test_post_request(openmotics_cloud) -> None:
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"key": "value"}

    openmotics_cloud.session.request = AsyncMock(return_value=mock_response)

    response = await openmotics_cloud.post("/test", data={"data": "test"})
    assert response == {"key": "value"}

    args, kwargs = openmotics_cloud.session.request.call_args
    assert args[0] == "POST"
    assert kwargs["data"] == {"data": "test"}


@pytest.mark.asyncio
async def test_request_timeout(openmotics_cloud) -> None:
    openmotics_cloud.session.request.side_effect = TimeoutError()

    with pytest.raises(OpenMoticsConnectionTimeoutError):
        await openmotics_cloud.get("/test")


@pytest.mark.asyncio
async def test_request_connection_error(openmotics_cloud) -> None:
    openmotics_cloud.session.request.side_effect = aiohttp.ClientError("Error")

    with pytest.raises(OpenMoticsConnectionError):
        await openmotics_cloud.get("/test")


@pytest.mark.asyncio
async def test_invalid_token() -> None:
    session = AsyncMock(spec=aiohttp.ClientSession)
    cloud = OpenMoticsCloud(token=None, session=session)
    assert cloud.token is None


@pytest.mark.asyncio
async def test_invalid_url(openmotics_cloud) -> None:
    openmotics_cloud.session.request.side_effect = aiohttp.ClientError("Error")

    with pytest.raises(OpenMoticsConnectionError):
        await openmotics_cloud.get("https://invalid.url/test")


@pytest.mark.asyncio
async def test_get_request_with_params(openmotics_cloud) -> None:
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"key": "value"}

    openmotics_cloud.session.request = AsyncMock(return_value=mock_response)

    response = await openmotics_cloud.get("/test", params={"param": "value"})
    assert response == {"key": "value"}

    _args, kwargs = openmotics_cloud.session.request.call_args
    assert kwargs["params"] == {"param": "value"}


@pytest.mark.asyncio
async def test_post_request_with_data(openmotics_cloud) -> None:
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"key": "value"}

    openmotics_cloud.session.request = AsyncMock(return_value=mock_response)

    response = await openmotics_cloud.post("/test", data={"data": "test"})
    assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_request_with_invalid_json(openmotics_cloud) -> None:
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/plain"}
    mock_response.text.return_value = "Invalid JSON"

    openmotics_cloud.session.request = AsyncMock(return_value=mock_response)

    response = await openmotics_cloud.get("/test")
    assert response == "Invalid JSON"


@pytest.mark.asyncio
async def test_request_with_404_error(openmotics_cloud) -> None:
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.headers = {}
    mock_response.raise_for_status = MagicMock()
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=(), status=404, message="Not Found", headers={}
    )

    openmotics_cloud.session.request = AsyncMock(return_value=mock_response)

    with pytest.raises(OpenMoticsConnectionError):
        await openmotics_cloud.get("/test")


@pytest.mark.asyncio
async def test_request_with_500_error(openmotics_cloud) -> None:
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.headers = {}
    mock_response.raise_for_status = MagicMock()
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=(), status=500, message="Server Error", headers={}
    )

    openmotics_cloud.session.request = AsyncMock(return_value=mock_response)

    with pytest.raises(OpenMoticsConnectionError):
        await openmotics_cloud.get("/test")


@pytest.mark.asyncio
async def test_close_session(openmotics_cloud) -> None:
    openmotics_cloud._close_session = True
    session_mock = openmotics_cloud.session
    await openmotics_cloud.close()
    session_mock.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_installation_id_property(openmotics_cloud) -> None:
    openmotics_cloud.installation_id = 123
    assert openmotics_cloud.installation_id == 123


@pytest.mark.asyncio
async def test_user_agent(openmotics_cloud) -> None:
    assert openmotics_cloud.user_agent.startswith("PyHAOpenMotics/")


@pytest.mark.asyncio
async def test_init_options() -> None:
    session = AsyncMock(spec=aiohttp.ClientSession)
    cloud = OpenMoticsCloud(
        token="test_token",
        session=session,
        installation_id=999,
        base_url="https://custom.url/api",
    )
    assert cloud.token == "test_token"
    assert cloud.session is session
    assert cloud.installation_id == 999
    assert cloud.base_url == "https://custom.url/api"


@pytest.mark.asyncio
async def test_get_url(openmotics_cloud) -> None:
    url = await openmotics_cloud._get_url("/test")
    assert url == "https://api.openmotics.com/api/v1.1/test"

    openmotics_cloud.base_url = "https://custom.url"
    url_custom = await openmotics_cloud._get_url("/test")
    assert url_custom == "https://custom.url/test"

    url_wss = await openmotics_cloud._get_url("/test", scheme="wss")
    assert url_wss == "wss://custom.url/test"


@pytest.mark.asyncio
async def test_get_auth_headers(openmotics_cloud) -> None:
    headers = await openmotics_cloud._get_auth_headers()
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_token"
    assert "Accept" in headers
    assert headers["Accept"] == "application/json"


@pytest.mark.asyncio
async def test_ws_connection_url(openmotics_cloud) -> None:
    url = await openmotics_cloud._get_ws_connection_url()
    assert url == "wss://api.openmotics.com/api/v1.1/ws/events"


@pytest.mark.asyncio
async def test_ws_headers(openmotics_cloud) -> None:
    import base64

    headers = await openmotics_cloud._get_ws_headers()
    assert "Sec-WebSocket-Protocol" in headers
    encoded_token = base64.b64encode(b"test_token").decode()
    assert headers["Sec-WebSocket-Protocol"] == f"authorization.bearer.{encoded_token}"
    assert "Sec-WebSocket-extensions" in headers


@pytest.mark.asyncio
async def test_ws_headers_with_extra_headers(openmotics_cloud) -> None:
    extra_headers = {"X-Test": "True"}
    headers = await openmotics_cloud._get_ws_headers(extra_headers)
    assert "X-Test" in headers
    assert headers["X-Test"] == "True"
    assert "Sec-WebSocket-Protocol" in headers


@pytest.mark.asyncio
async def test_installations_property(openmotics_cloud) -> None:
    from pyhaopenmotics.cloud.installations import OpenMoticsInstallations

    installations = openmotics_cloud.installations
    assert isinstance(installations, OpenMoticsInstallations)
    assert installations._omcloud == openmotics_cloud
