"""Module containing a generic Client for the OpenMotics API."""

# from pyhaopenmotics.cloud.models import Installation

from .errors import (
    AuthenticationError,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
    OpenMoticsError,
)
from .localgateway import LocalGateway
from .openmoticscloud import OpenMoticsCloud

__all__ = [
    "AuthenticationError",
    "LocalGateway",
    "OpenMoticsCloud",
    "OpenMoticsConnectionError",
    "OpenMoticsConnectionSslError",
    "OpenMoticsConnectionTimeoutError",
    "OpenMoticsError",
]
