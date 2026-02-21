"""Module containing a generic Client for the OpenMotics API."""

from __future__ import annotations

import asyncio

# import abc
import logging
import socket
from typing import TYPE_CHECKING, Any, TypeVar

import aiohttp
import stamina
from yarl import URL

from pyhaopenmotics.__version__ import __version__
from pyhaopenmotics.client.errors import (
    AuthenticationError,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
)

if TYPE_CHECKING:
    import ssl
    from collections.abc import Awaitable, Callable
    from typing import Self

_LOGGER = logging.getLogger(__name__)

StrOrURL = str | URL
T = TypeVar("T")


class BaseClient:
    """Base client for interacting with the OpenMotics API."""

    _inputs_class: type | None = None
    _outputs_class: type | None = None
    _groupactions_class: type | None = None
    _lights_class: type | None = None
    _sensors_class: type | None = None
    _energysensors_class: type | None = None
    _shutters_class: type | None = None
    _thermostats_class: type | None = None

    def __init__(
        self,
        *,
        token: str | None = None,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession | None = None,
        token_refresh_method: Callable[[], Awaitable[str]] | None = None,
        verify_ssl: bool = False,
        ssl_context: ssl.SSLContext | None = None,
        port: int = 443,
    ) -> None:
        """Initialize connection with the OpenMotics API.

        Args:
            token: Authentication token.
            request_timeout: Max timeout (seconds) for API requests.
            session: Optional, shared, aiohttp client session.
            token_refresh_method: Async function to refresh the token.
            verify_ssl: Whether to verify SSL certificates.
            ssl_context: Optional SSL context.
            port: API port (usually 443 or 3000).

        """
        self.user_agent = f"PyHAOpenMotics/{__version__}"
        self.token = token.strip() if token else None
        self.token_expires_at: float = 0.0

        self.request_timeout = request_timeout
        self.session = session
        self._close_session = False
        self.verify_ssl = verify_ssl
        self.ssl_context = ssl_context
        self.port = port

        self.token_refresh_method = token_refresh_method

    def _get_api_module(self, module_class: type[T] | None, name: str) -> T:
        """Get an instance of an API module."""
        if module_class is None:
            msg = f"{name} class not defined"
            raise NotImplementedError(msg)
        return module_class(self)  # type: ignore[call-arg]

    @property
    def inputs(self) -> Any:
        """Get inputs module."""
        return self._get_api_module(self._inputs_class, "Inputs")

    @property
    def outputs(self) -> Any:
        """Get outputs module."""
        return self._get_api_module(self._outputs_class, "Outputs")

    @property
    def groupactions(self) -> Any:
        """Get group actions module."""
        return self._get_api_module(self._groupactions_class, "Groupactions")

    @property
    def lights(self) -> Any:
        """Get lights module."""
        return self._get_api_module(self._lights_class, "Lights")

    @property
    def sensors(self) -> Any:
        """Get sensors module."""
        return self._get_api_module(self._sensors_class, "Sensors")

    @property
    def energysensors(self) -> Any:
        """Get energy sensors module."""
        return self._get_api_module(self._energysensors_class, "Energy sensors")

    @property
    def shutters(self) -> Any:
        """Get shutters module."""
        return self._get_api_module(self._shutters_class, "Shutters")

    @property
    def thermostats(self) -> Any:
        """Get thermostats module."""
        return self._get_api_module(self._thermostats_class, "Thermostats")

    @stamina.retry(on=OpenMoticsConnectionError, attempts=3)
    async def _request(
        self,
        path: str,
        *,
        method: str = aiohttp.hdrs.METH_POST,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        scheme: str = "https",
        **kwargs: Any,
    ) -> Any:
        """Make a request to the OpenMotics API.

        Retries on connection errors.

        Args:
            path: API path.
            method: HTTP method (default: POST).
            data: JSON data to send.
            headers: HTTP headers.
            scheme: URL scheme (http/https).
            **kwargs: Extra arguments for httpx.request.

        Returns:
            Response JSON or text.

        Raises:
            OpenMoticsConnectionError: Communication error.
            OpenMoticsConnectionSslError: SSL error.
            OpenMoticsConnectionTimeoutError: Timeout error.
            AuthenticationError: Token expired or invalid.

        """
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()

        url = await self._get_url(path=path, scheme=scheme)

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    data=data,
                    ssl=self.ssl_context,  # pyright: ignore [reportArgumentType]
                    headers=headers,
                    **kwargs,
                )

            if _LOGGER.isEnabledFor(logging.DEBUG):
                body = await response.text()
                _LOGGER.debug(
                    "Request with status=%s, body=%s",
                    response.status,
                    body,
                )

            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return await response.json()
            return await response.text()

        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to OpenMotics API."
            raise OpenMoticsConnectionTimeoutError(msg) from exception
        except aiohttp.ClientConnectorSSLError as exception:
            # pylint: disable=bad-exception-context
            msg = "Error with SSL certificate."
            raise OpenMoticsConnectionSslError(msg) from exception
        except aiohttp.ClientResponseError as exception:
            if exception.status in [401, 403]:
                raise AuthenticationError from exception
            msg = f"Error occurred while communicating with OpenMotics API: {exception.status}, message='{exception.message}'"
            raise OpenMoticsConnectionError(msg) from exception
        except (socket.gaierror, aiohttp.ClientError) as exception:
            msg = "Error occurred while communicating with OpenMotics API."
            raise OpenMoticsConnectionError(msg) from exception
        except Exception as exception:
            msg = f"Unexpected error occurred while communicating with OpenMotics API: {exception}"
            raise OpenMoticsConnectionError(msg) from exception

    async def get_token(self) -> None:
        """Login to the gateway and set the token."""
        raise NotImplementedError

    async def get(self, path: str, headers: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Make a GET request.

        Args:
            path: API path.
            headers: Optional HTTP headers.
            **kwargs: Extra arguments for request.

        Returns:
            Response JSON or text.

        """
        headers = await self._get_auth_headers(headers)
        return await self._request(
            path,
            method=aiohttp.hdrs.METH_GET,
            headers=headers,
            **kwargs,
        )

    async def post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Make a POST request.

        Args:
            path: API path.
            data: JSON data to send.
            headers: Optional HTTP headers.
            **kwargs: Extra arguments for request.

        Returns:
            Response JSON or text.

        """
        headers = await self._get_auth_headers(headers)
        return await self._request(
            path,
            method=aiohttp.hdrs.METH_POST,
            data=data,
            headers=headers,
            **kwargs,
        )

    async def _get_url(self, path: str, scheme: str = "https") -> str:
        """Construct the full URL.

        Args:
            path: API path.
            scheme: URL scheme.

        Returns:
            Full URL string.

        """
        raise NotImplementedError

    async def _get_ws_connection_url(self) -> str:
        """Get the WebSocket connection URL."""
        raise NotImplementedError

    async def _get_auth_headers(
        self,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get headers with authentication token.

        Args:
            headers: Base headers.

        Returns:
            Headers with User-Agent and Authorization.

        """
        headers = headers or {}
        headers["User-Agent"] = self.user_agent
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def close(self) -> None:
        """Close the client session."""
        if self.session and self._close_session:
            await self.session.close()
            self.session = None

    async def __aenter__(self) -> Self:
        """Async context manager enter."""
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        """Async context manager exit."""
        await self.close()
