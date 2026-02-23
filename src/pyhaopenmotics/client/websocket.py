"""Code for communication with the OpenMotics websocket."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    import ssl

    from pyhaopenmotics.client.localgateway import LocalGateway
    from pyhaopenmotics.client.openmoticscloud import OpenMoticsCloud

from pyhaopenmotics.helpers import get_ssl_context

_LOGGER = logging.getLogger(__name__)

BaseClientTypes = Union[
    "LocalGateway",
    "OpenMoticsCloud",
]


class WebsocketClient:
    """Represents the websocket class."""

    def __init__(
        self,
        baseclient: BaseClientTypes,
        verify_ssl: bool = False,
        ssl_context: ssl.SSLContext | None = None,
    ) -> None:
        """Initialize the websocket."""
        self.baseclient = baseclient
        self.connection_url: str = ""

        self.verify_ssl = verify_ssl
        if ssl_context is not None:
            self.ssl_context = ssl_context
        else:
            self.ssl_context = get_ssl_context(verify_ssl=self.verify_ssl)

    # # https://websockets.readthedocs.io/en/stable/reference/client.html#opening-a-connection
    # async def connect(  # type: ignore[no-untyped-def]
    #     self,
    #     # processor:
    #     #     # Callable[[List[WebSocketMessage]], Awaitable],
    #     #     Callable[[Union[str, bytes]], Awaitable],
    #     close_timeout: int = 1,
    #     **kwargs,
    # ) -> None:
    #     """Connect to websocket server and run `processor(msg)` on every new `msg`.

    #     :param processor: The callback to process messages.
    #     :param close_timeout: How long to wait for handshake when calling .close.
    #     :raises AuthError: If invalid API key is supplied.
    #     """
    #     self.connection_url = await self.baseclient._get_ws_connection_url()

    #     _LOGGER.debug("connect: %s", self.connection_url)
    #     # darwin needs some extra <3
    #     # ssl_context = None
    #     # if self.connection_url.startswith("wss://"):
    #     #     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    #     #     if self.tls:

    #     #     ssl_context.load_verify_locations(certifi.where())

    #     extra_headers = await self.baseclient._get_ws_headers()

    #     try:
    #         async with websockets.connect(
    #             uri=self.connection_url,
    #             extra_headers=extra_headers,
    #             ssl=self.ssl_context,
    #             # ping_interval=10,
    #             # ping_timeout=10,
    #         ) as websocket:
    #             _LOGGER.info("WebSocket Opened.")

    #             await asyncio.sleep(1)

    #             # _LOGGER.info(json.loads(await websocket.recv()))
    #             # _LOGGER.info("websocket client connected. looping...")

    #             while self.loop:  # type: ignore[attr-defined]
    #                 data = json.loads(await websocket.recv())
    #                 if "event" not in data:
    #                     continue

    #     #                 try:
    #     #                     self.ws_handler(self, data)
    #     #                 except:
    #     #                     _LOGGER.error("".join(traceback.format_exc()))

    #     except websockets.WebSocketException:
    #         pass

    #     return None

    # async def disconnect(self) -> None:
    #     """Close the websocket."""
    #     await self._websocket.close(code=1000, reason="Handle disconnect request")

    # async def consumer_handler(self, websocket, on_data: Callable):
    #     """Used when data is transmitted using the websocket."""
    #     async for message in websocket:
    #         try:
    #             event_data = LivisiEvent.parse_raw(message)
    #         except ValidationError:
    #             continue

    #         if "device" in event_data.source:
    #             event_data.source = event_data.source.replace("/device/", "")
    #         if event_data.properties is None:
    #             continue

    #         # if event_data.type == EVENT_STATE_CHANGED:
    #         #     if ON_STATE in event_data.properties.keys():
    #         #         event_data.onState = event_data.properties.get(ON_STATE)
    #         #     elif VALUE in event_data.properties.keys() and isinstance(
    #         #         event_data.properties.get(VALUE), bool
    #         #     ):
    #         #         event_data.onState = event_data.properties.get(VALUE)
    #         #     if SET_POINT_TEMPERATURE in event_data.properties.keys():
    #         #         event_data.vrccData = event_data.properties.get(
    #         #             SET_POINT_TEMPERATURE
    #         #         )
    #         #     elif POINT_TEMPERATURE in event_data.properties.keys():
    #         #         event_data.vrccData = event_data.properties.get(POINT_TEMPERATURE)
    #         #     elif TEMPERATURE in event_data.properties.keys():
    #         #         event_data.vrccData = event_data.properties.get(TEMPERATURE)
    #         #     elif HUMIDITY in event_data.properties.keys():
    #         #         event_data.vrccData = event_data.properties.get(HUMIDITY)
    #         #     if LUMINANCE in event_data.properties.keys():
    #         #         event_data.luminance = event_data.properties.get(LUMINANCE)
    #         #     if IS_REACHABLE in event_data.properties.keys():
    #         #         event_data.isReachable = event_data.properties.get(IS_REACHABLE)
    #         #     if IS_OPEN in event_data.properties.keys():
    #         #         event_data.isOpen = event_data.properties.get(IS_OPEN)
    #         # elif event_data.type == EVENT_BUTTON_PRESSED:
    #         #     if KEY_INDEX in event_data.properties.keys():
    #         #         event_data.keyIndex = event_data.properties.get(KEY_INDEX)
    #         #         event_data.isLongKeyPress = (
    #         #             KEY_PRESS_LONG == event_data.properties.get(KEY_PRESS_TYPE)
    #         #         )
    #         on_data(event_data)
