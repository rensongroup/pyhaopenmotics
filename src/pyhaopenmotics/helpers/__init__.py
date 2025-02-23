"""Asynchronous Python client for the OpenMotics API."""

import logging
import ssl
from typing import Any


def get_key_for_word(dictionary: dict[str, Any], word: str) -> Any:
    """Return the key with value.

    Args:
    ----
        dictionary: dict
        word: str

    Returns:
    -------
        Any

    """
    try:
        for key, value in dictionary.items():
            if value == word:
                return key

    except KeyError as err:
        msg = f"Key Error: {err}"
        logging.exception(msg)

    return None


def merge_dicts(list_a: list[Any], dkey: str, list_b: list[Any]) -> list[Any]:
    """Merge list_b into the key 'dkey' of list_a.

    Args:
    ----
        dkey: str
        list_a: list
        list_b: list

    Returns:
    -------
        result: list

    # noqa: E800
    2 list are given:
    list_a = [{'name': 'Vijver', 'room': 255, 'module_type': 'O', 'id': 0},
             {'name': 'Boom', 'room': 255, 'module_type': 'O', 'id': 1}]
    list_b = [{'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 0, 'locked': False},
             {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 1, 'locked': False}]
    The dictionaries in list_b are merged under the key 'dkey' into the
    dictionaries of list_a
    result = [{'name': 'Vijver', 'room': 255, 'module_type': 'O', 'id': 0,
                'status': {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 0,
                locked': False}},
              {'name': 'Boom', 'room': 255, 'module_type': 'O', 'id': 1,
              status': {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 1,
              'locked': False}}]

    """
    if len(list_a) == 0:
        return []
    if len(list_b) == 0:
        return list_a
    return [d1 | {dkey: d2} for d1, d2 in zip(list_a, list_b, strict=False)]


def get_ssl_context(*, verify_ssl: bool = True) -> ssl.SSLContext:
    """Get ssl_context for local gateway.

    Args:
    ----
        verify_ssl: bool

    Returns:
    -------
        ssl.SSLContext

    """
    if verify_ssl:
        ssl_context = ssl.create_default_context()
    else:
        # self signed certificates
        # ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # ssl_context.options &= ~ssl.OP_NO_SSLv3
        # ssl_context.minimum_version = ssl.TLSVersion.TLSv1
        # ssl_context.set_ciphers("AES256-SHA")  # enables weaker ciphers and protocols
    return ssl_context
