"""Module containing a LocalGateway Client for the OpenMotics API."""

from __future__ import annotations

import asyncio
import logging
import socket
import time
from typing import TYPE_CHECKING, Any

import aiohttp
from yarl import URL

from .__version__ import __version__
from .errors import (
    AuthenticationError,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
)
from .helpers import get_ssl_context
from .openmoticsgw.energy import OpenMoticsEnergySensors
from .openmoticsgw.groupactions import OpenMoticsGroupActions
from .openmoticsgw.inputs import OpenMoticsInputs
from .openmoticsgw.lights import OpenMoticsLights
from .openmoticsgw.outputs import OpenMoticsOutputs
from .openmoticsgw.sensors import OpenMoticsSensors
from .openmoticsgw.shutters import OpenMoticsShutters
from .openmoticsgw.thermostats import OpenMoticsThermostats

if TYPE_CHECKING:
    import ssl


_LOGGER = logging.getLogger(__name__)

LOCAL_TOKEN_EXPIRES_IN = 3600
CLOCK_OUT_OF_SYNC_MAX_SEC = 20


class LocalGateway:
    """Docstring."""

    _close_session: bool = False

    def __init__(
        self,
        username: str,
        password: str,
        localgw: str,
        *,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession | None = None,
        tls: bool = False,
        ssl_context: ssl.SSLContext | None = None,
        port: int = 443,
    ) -> None:
        """Initialize connection with the OpenMotics LocalGateway API.

        Args:
        ----
            localgw: Hostname or IP address of the AdGuard Home instance.
            password: Password for HTTP auth, if enabled.
            port: Port on which the API runs, usually 3000.
            request_timeout: Max timeout to wait for a response from the API.
            session: Optional, shared, aiohttp client session.
            tls: True, when TLS/SSL should be used.
            username: Username for HTTP auth, if enabled.
            ssl_context: ssl.SSLContext.

        """
        self.session = session
        self.token = None
        self.token_expires_at: float = 0

        self.localgw = localgw
        self.password = password
        self.port = port
        self.request_timeout = request_timeout
        self.tls = tls
        self.username = username
        if ssl_context is not None:
            self.ssl_context = ssl_context
        else:
            self.ssl_context = get_ssl_context(verify_ssl=self.tls)

        self.user_agent = f"PyHAOpenMotics/{__version__}"

        self.auth = None
        if self.username and self.password:
            _LOGGER.debug("LocalGateway setting self.auth")
            self.auth = {"username": self.username, "password": self.password}

    # @backoff.on_exception(
    #   backoff.expo, OpenMoticsConnectionError, max_tries=3, logger=None)
    async def _request(
        self,
        path: str,
        *,
        method: str = aiohttp.hdrs.METH_POST,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
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
        url = URL.build(scheme="https", host=self.localgw, port=self.port, path="/").join(URL(path))

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                resp = await self.session.request(
                    method,
                    url,
                    data=data,
                    ssl=self.ssl_context,
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
            # Expired certificate / Date ISSUE
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

    async def exec_action(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
        ----
            path: path
            data: dict
            headers: dict

        Returns:
        -------
            response json or text

        """
        # Try to execute the action.
        return await self._request(
            path,
            method=aiohttp.hdrs.METH_POST,
            data=data,
            headers=await self._get_auth_headers(headers),
        )

    async def get_token(self) -> None:
        """Login to the gateway: sets the token in the connector."""
        resp = await self._request(
            path="login",
            data=self.auth,
        )
        if resp["success"] is True:
            self.token = resp["token"]
            self.token_expires_at = time.time() + LOCAL_TOKEN_EXPIRES_IN
        else:
            self.token = None
            self.token_expires_at = 0

    async def subscribe_webhook(self, installation_id: str) -> None:
        """Register a webhook with OpenMotics for live updates.

        Args:
        ----
            installation_id: int

        """
        # Register webhook
        await self._request(
            "/ws/events",
            method=aiohttp.hdrs.METH_POST,
            data={
                "action": "set_subscription",
                "types": [
                    "OUTPUT_CHANGE",
                    "SHUTTER_CHANGE",
                    "THERMOSTAT_CHANGE",
                    "THERMOSTAT_GROUP_CHANGE",
                ],
                "installation_ids": [installation_id],
            },
            headers=await self._get_auth_headers(),
        )

    async def unsubscribe_webhook(self) -> None:
        """Delete all webhooks for this application ID."""
        await self._request(
            "/ws/events",
            method=aiohttp.hdrs.METH_DELETE,
            headers=await self._get_auth_headers(),
        )

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
        if self.token is None or self.token_expires_at < time.time() + CLOCK_OUT_OF_SYNC_MAX_SEC:
            await self.get_token()

        if headers is None:
            headers = {}

        headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
            },
        )
        return headers

    @property
    def inputs(self) -> OpenMoticsInputs:
        """Get outputs.

        Returns
        -------
            OpenMoticsOutputs

        """
        return OpenMoticsInputs(self)

    @property
    def outputs(self) -> OpenMoticsOutputs:
        """Get outputs.

        Returns
        -------
            OpenMoticsOutputs

        """
        return OpenMoticsOutputs(self)

    @property
    def groupactions(self) -> OpenMoticsGroupActions:
        """Get groupactions.

        Returns
        -------
            OpenMoticsGroupActions

        """
        return OpenMoticsGroupActions(self)

    @property
    def lights(self) -> OpenMoticsLights:
        """Get lights.

        Returns
        -------
            OpenMoticsLights

        """
        # implemented to be compatible with cloud
        return OpenMoticsLights(self)

    @property
    def sensors(self) -> OpenMoticsSensors:
        """Get sensors.

        Returns
        -------
            OpenMoticsSensors

        """
        return OpenMoticsSensors(self)

    @property
    def energysensors(self) -> OpenMoticsEnergySensors:
        """Get energy sensors.

        Returns
        -------
            OpenMoticsEnergySensors

        """
        return OpenMoticsEnergySensors(self)

    @property
    def shutters(self) -> OpenMoticsShutters:
        """Get shutters.

        Returns
        -------
            OpenMoticsShutters

        """
        return OpenMoticsShutters(self)

    @property
    def thermostats(self) -> OpenMoticsThermostats:
        """Get thermostats.

        Returns
        -------
            OpenMoticsThermostats

        """
        return OpenMoticsThermostats(self)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Any:
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
