"""Module containing a LocalGateway Client for the OpenMotics API."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from yarl import URL

from pyhaopenmotics.client.baseclient import BaseClient
from pyhaopenmotics.helpers import get_ssl_context
from pyhaopenmotics.openmoticsgw.energy import OpenMoticsEnergySensors
from pyhaopenmotics.openmoticsgw.groupactions import OpenMoticsGroupActions
from pyhaopenmotics.openmoticsgw.inputs import OpenMoticsInputs
from pyhaopenmotics.openmoticsgw.lights import OpenMoticsLights
from pyhaopenmotics.openmoticsgw.outputs import OpenMoticsOutputs
from pyhaopenmotics.openmoticsgw.sensors import OpenMoticsSensors
from pyhaopenmotics.openmoticsgw.shutters import OpenMoticsShutters
from pyhaopenmotics.openmoticsgw.thermostats import OpenMoticsThermostats

if TYPE_CHECKING:
    import ssl

    import aiohttp


_LOGGER = logging.getLogger(__name__)

LOCAL_TOKEN_EXPIRES_IN = 3600
CLOCK_OUT_OF_SYNC_MAX_SEC = 20


class LocalGateway(BaseClient):
    """Docstring."""

    _inputs_class = OpenMoticsInputs
    _outputs_class = OpenMoticsOutputs
    _groupactions_class = OpenMoticsGroupActions
    _lights_class = OpenMoticsLights
    _sensors_class = OpenMoticsSensors
    _energysensors_class = OpenMoticsEnergySensors
    _shutters_class = OpenMoticsShutters
    _thermostats_class = OpenMoticsThermostats

    def __init__(
        self,
        username: str,
        password: str,
        localgw: str,
        *,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession | None = None,
        verify_ssl: bool = False,
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
        super().__init__(
            request_timeout=request_timeout,
            session=session,
            port=port,
            verify_ssl=verify_ssl,
            ssl_context=ssl_context,
        )

        self.localgw = localgw
        self.password = password
        self.username = username

        if ssl_context is not None:
            self.ssl_context = ssl_context
        else:
            self.ssl_context = get_ssl_context(verify_ssl=verify_ssl)

        self.auth = None
        if self.username and self.password:
            _LOGGER.debug("LocalGateway setting self.auth")
            self.auth = {"username": self.username, "password": self.password}

    async def exec_action(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Make get request using the underlying httpx client.

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
        return await self.post(
            path,
            data=data,
            headers=headers,
        )

    async def get_token(self) -> None:
        """Login to the gateway: sets the token in the connector."""
        response = await self._request(
            path="login",
            method="POST",
            data=self.auth,
        )
        if response["success"] is True:
            self.token = response["token"]
            self.token_expires_at = time.time() + LOCAL_TOKEN_EXPIRES_IN
        else:
            self.token = None
            self.token_expires_at = 0

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
        return str(
            URL.build(scheme=scheme, host=self.localgw, port=self.port, path="/").join(URL(path)),
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

        headers = await super()._get_auth_headers(headers)
        headers["Accept"] = "application/json, text/plain, */*"

        return headers

    async def _get_ws_connection_url(self) -> str:
        return await self._get_url(
            path="/ws_events",
            scheme="wss",
        )

    # async def _get_ws_headers(
    #     self,
    #     headers: dict[str, Any] | None = None,
    # ) -> dict[str, Any]:
    #     """Update the auth headers to include a working token.

    #     Args:
    #     ----
    #         headers: dict

    #     Returns:
    #     -------
    #         headers

    #     """
    #     if self.token is None or self.token_expires_at < time.time() + CLOCK_OUT_OF_SYNC_MAX_SEC:
    #         await self.get_token()

    #     if headers is None:
    #         headers = {}

    #     base64_message = str(base64.b64encode(self.token))

    #     headers.update(
    #         {
    #             # "User-Agent": self.user_agent,
    #             "Sec-WebSocket-Protocol": f"authorization.bearer.{base64_message}",
    #             # "Sec-WebSocket-Extensions": "permessage-deflate",
    #             # "host": self.localgw,
    #             # "Origin": self.localgw,
    #             "Connection": "Upgrade",
    #             "Upgrade": "websocket",
    #             # "accept-encoding": "gzip, deflate, br",
    #             # "cache-control": "no-cache",
    #             # "pragma": "no-cache",
    #             # # "Sec-Fetch-Dest": "websocket",
    #             # "Sec-Fetch-Mode": "websocket",
    #             # "Sec-Fetch-site": "same-site",
    #             # "user-agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    #             #    AppleWebKit/537.36 (KHTML, like Gecko)
    #             #    Chrome/109.0.0.0 Safari/537.36",
    #         },
    #     )
    #     return headers

    # @property
    # def connected(self) -> bool:
    #     """Return if we are connect to the WebSocket of OpenMotics.

    #     Returns
    #     -------
    #         True if we are connected to the WebSocket,
    #         False otherwise.
    #     """
    #     return self._wsclient is not None and not self._wsclient.closed
