"""Module HTTP communication with the OpenMotics API."""

from pyhaopenmotics.cloud.models import Installation

from .client.errors import (
    AuthenticationError,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
    OpenMoticsError,
)
from .client.localgateway import LocalGateway
from .client.openmoticscloud import OpenMoticsCloud
from .helpers import get_ssl_context

__all__ = [
    "AuthenticationError",
    "Installation",
    "LocalGateway",
    "OpenMoticsCloud",
    "OpenMoticsConnectionError",
    "OpenMoticsConnectionSslError",
    "OpenMoticsConnectionTimeoutError",
    "OpenMoticsError",
    "get_ssl_context",
]
