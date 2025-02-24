"""Module containing a OpenMoticsCloud Client for the OpenMotics API."""

from __future__ import annotations

import logging
import socket
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout
import backoff
from yarl import URL

from .__version__ import __version__
from .cloud.energy import OpenMoticsEnergySensors
from .cloud.groupactions import OpenMoticsGroupActions
from .cloud.inputs import OpenMoticsInputs
from .cloud.installations import OpenMoticsInstallations
from .cloud.lights import OpenMoticsLights
from .cloud.outputs import OpenMoticsOutputs
from .cloud.sensors import OpenMoticsSensors
from .cloud.shutters import OpenMoticsShutters
from .cloud.thermostats import OpenMoticsThermostats
from .const import CLOUD_API_URL
from .errors import OpenMoticsConnectionError, OpenMoticsConnectionTimeoutError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from .cloud.models.installation import Installation


_LOGGER = logging.getLogger(__name__)


class OpenMoticsCloud:
    """Docstring."""

    _installations: list[Installation] | None
    _close_session: bool = False

    def __init__(
        self,
        token: str,
        *,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession | None = None,
        token_refresh_method: Callable[[], Awaitable[str]] | None = None,
        installation_id: int | None = None,
        base_url: str = CLOUD_API_URL,
    ) -> None:
        """Initialize connection with the OpenMotics Cloud API.

        Args:
        ----
            token: str
            request_timeout: int
            session: aiohttp.client.ClientSession
            token_refresh_method: token refresh function
            installation_id: int
            base_url: str

        """
        self.session = session
        self.token = None if token is None else token.strip()
        self._installation_id = installation_id
        self.base_url = base_url

        self.request_timeout = request_timeout
        self.token_refresh_method = token_refresh_method
        self.user_agent = f"PyHAOpenMotics/{__version__}"

    @property
    def installation_id(self) -> int | None:
        """Get installation id.

        Returns
        -------
            The installation id that will be used for this session.

        """
        return self._installation_id

    @installation_id.setter
    def installation_id(self, installation_id: int) -> None:
        """Set installation id.

        Args:
        ----
            installation_id: The installation id that will be used
                for this session.

        """
        self._installation_id = installation_id

    @backoff.on_exception(backoff.expo, OpenMoticsConnectionError, max_tries=3, logger=None)
    async def _request(
        self,
        path: str,
        *,
        method: str = aiohttp.hdrs.METH_GET,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Make post request using the underlying aiohttp clientsession.

        with the default timeout of 15s. in case of retryable exceptions,
        requests are retryed for up to 10 times or 5 minutes.

        Args:
        ----
            path: path
            method: get of post
            params: dict
            **kwargs: extra args

        Returns:
        -------
            response json or text

        Raises:
        ------
            OpenMoticsConnectionError: An error occurred while communication with
                the OpenMotics API.
            OpenMoticsConnectionTimeoutError: A timeout occurred while communicating
                with the OpenMotics API.

        """
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()

        url = str(URL(f"{self.base_url}{path}"))

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

        if params:
            for key, value in params.items():
                if isinstance(value, bool):
                    params[key] = str(value).lower()

        try:
            async with async_timeout.timeout(self.request_timeout):
                resp = await self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
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
            msg = "Timeout occurred while connecting to OpenMotics API"
            raise OpenMoticsConnectionTimeoutError(msg) from exception
        except (
            aiohttp.ClientError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with OpenMotics API."
            raise OpenMoticsConnectionError(msg) from exception

        if "application/json" in resp.headers.get("Content-Type", ""):
            return await resp.json()

        return await resp.text()

    async def get(self, path: str, **kwargs: Any) -> Any:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
        ----
            path: string
            **kwargs: any

        Returns:
        -------
            response json or text

        """
        return await self._request(
            path,
            method=aiohttp.hdrs.METH_GET,
            **kwargs,
        )

    async def post(self, path: str, **kwargs: Any) -> Any:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
        ----
            path: path
            **kwargs: extra args

        Returns:
        -------
            response json or text

        """
        return await self._request(
            path,
            method=aiohttp.hdrs.METH_POST,
            **kwargs,
        )

    async def subscribe_webhook(self) -> None:
        """Register a webhook with OpenMotics for live updates."""
        # Register webhook
        await self._request(
            "/ws/events",
            method=aiohttp.hdrs.METH_POST,
            data={
                "type": "ACTION",
                "data": {
                    "action": "set_subscription",
                    "types": [
                        "OUTPUT_CHANGE",
                        "SENSOR_CHANGE",
                        "SHUTTER_CHANGE",
                        "THERMOSTAT_CHANGE",
                        "THERMOSTAT_GROUP_CHANGE",
                        "VENTILATION_CHANGE",
                    ],
                    "installation_ids": [self.installation_id],
                },
            },
        )

    async def unsubscribe_webhook(self) -> None:
        """Delete all webhooks for this application ID."""
        await self._request(
            "/ws/events",
            method=aiohttp.hdrs.METH_DELETE,
        )

    @property
    def installations(self) -> OpenMoticsInstallations:
        """Get installations.

        Returns
        -------
            OpenMoticsInstallations

        """
        return OpenMoticsInstallations(self)

    @property
    def inputs(self) -> OpenMoticsInputs:
        """Get inputs.

        Returns
        -------
            OpenMoticsInputs

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
            OpenMoticsCloud: The OpenMoticsCloud object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            *_exc_info: Exec type.

        """
        await self.close()
