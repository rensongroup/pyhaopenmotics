"""Module containing a generic Client for the OpenMotics API."""

from __future__ import annotations

import asyncio

# import abc
import logging
import socket
from typing import TYPE_CHECKING, Any

import aiohttp
import backoff

# import websockets
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


class BaseClient:
    """Docstring."""

    _wsclient: aiohttp.ClientWebSocketResponse | None = None
    _close_session: bool = False

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
        """Initialize connection with the OpenMotics LocalGateway API.

        Args:
        ----
            token: str
            session: aiohttp.client.ClientSession
            token_refresh_method: token refresh function
            port: Port on which the API runs, usually 3000.
            request_timeout: Max timeout to wait for a response from the API.
            session: Optional, shared, aiohttp client session.
            tls: True, when TLS/SSL should be used.
            username: Username for HTTP auth, if enabled.
            ssl_context: ssl.SSLContext.

        """
        self.user_agent = f"PyHAOpenMotics/{__version__}"
        self.token = None if token is None else token.strip()
        self.token_expires_at: float = 0

        self.request_timeout = request_timeout
        self.session = session
        self.verify_ssl = verify_ssl
        self.ssl_context = ssl_context
        self.port = port

        self.token_refresh_method = token_refresh_method

    @backoff.on_exception(backoff.expo, OpenMoticsConnectionError, max_tries=3, logger=None)
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
        """Make post request using the underlying aiohttp clientsession.

        with the default timeout of 15s. in case of retryable exceptions,
        requests are retryed for up to 10 times or 5 minutes.

        Args:
        ----
            path: path
            method: post
            data: dict
            headers: dict
            scheme: str
            **kwargs: extra args

        Returns:
        -------
            response json or text

        Raises:
        ------
            OpenMoticsConnectionError: An error occurred while communication with
                the OpenMotics API.
            OpenMoticsConnectionSslError: Error with SSL certificates.
            OpenMoticsConnectionTimeoutError: A timeout occurred while communicating
                with the OpenMotics API.
            AuthenticationException: raised when token is expired.

        """
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()

        url = await self._get_url(
            path=path,
            scheme=scheme,
        )

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                resp = await self.session.request(
                    method,
                    url,
                    data=data,
                    ssl=self.ssl_context,  # pyright: ignore [reportArgumentType]
                    headers=headers,
                    **kwargs,
                )

            if _LOGGER.isEnabledFor(logging.DEBUG):
                body = await resp.text()
                _LOGGER.debug(
                    "Request with status=%s, body=%s",
                    resp.status,
                    body,
                )

            resp.raise_for_status()

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
            msg = "Error occurred while communicating with OpenMotics API."
            raise OpenMoticsConnectionError(msg) from exception
        except (socket.gaierror, aiohttp.ClientError) as exception:
            msg = "Error occurred while communicating with OpenMotics API."
            raise OpenMoticsConnectionError(msg) from exception

        if "application/json" in resp.headers.get("Content-Type", ""):
            return await resp.json()

        return await resp.text()

    # @property
    # def token(self) -> str:
    #     return self.token

    # @property.setter
    # def token(self, token: str | None is None) -> None:
    #     self.token = token

    async def get_token(self) -> None:
        """Login to the gateway: sets the token in the connector."""
        raise NotImplementedError

    async def _get_url(self, path: str, scheme: str = "https") -> str:
        """Update the auth headers to include a working token.

        Args:
        ----
            path: str
            scheme: str

        Returns:
        -------
            url: str

        """
        # Base class should implement this
        raise NotImplementedError

    async def _get_ws_connection_url(self) -> str:
        raise NotImplementedError

    async def _get_auth_headers(
        self,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update the auth headers to include a working token.

        Args:
        ----
            headers: dict

        Returns:
        -------
            headers

        """
        # Base class should implement this
        raise NotImplementedError

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            LocalGateway: The LocalGateway object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            *_exc_info: Exec type.

        """
        await self.close()
