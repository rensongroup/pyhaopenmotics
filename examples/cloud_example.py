#!/usr/bin/env python3
"""Cloud example.

How to use this script:
    export CLIENT_ID="dnfqsdfjqsjfqsdjfqf"
    export CLIENT_SECRET="djfqsdkfjqsdkfjqsdkfjqsdkfjkqsdjfkjdkfqjdskf"
    export INSTALLATION_ID="1" if you have multiple installations
    python cloud_example.py
"""

from __future__ import annotations

import asyncio
import logging
import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError as exc:
    msg = "You have to run 'pip install python-dotenv' first"
    raise ImportError(msg) from exc

try:
    from authlib.integrations.httpx_client import AsyncOAuth2Client
except ModuleNotFoundError as exc:
    msg = "You have to run 'pip install httpx authlib' first"
    raise ImportError(msg) from exc


from pyhaopenmotics import OpenMoticsCloud
from pyhaopenmotics.const import CLOUD_SCOPE, OAUTH2_TOKEN

# UNCOMMENT THIS TO SEE ALL THE HTTPX INTERNAL LOGGING
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log_format = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(log_format)
log.addHandler(console)


load_dotenv()

client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
installation_id = os.environ["INSTALLATION_ID"]


async def main() -> None:
    """Docstring."""
    token = None

    async with AsyncOAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        token_endpoint_auth_method="client_secret_post",  # noqa: S106 # nosec
        scope=CLOUD_SCOPE,
        token_endpoint=OAUTH2_TOKEN,
        grant_type="client_credentials",
    ) as httpx_session:
        token = await httpx_session.fetch_token(
            url=OAUTH2_TOKEN,
            grant_type="client_credentials",
        )
        access_token = token.get("access_token")

        omclient = OpenMoticsCloud(token=access_token)

        installations = await omclient.installations.get_all()

        if installation_id:
            i_id = int(installation_id)
        else:
            i_id = installations[0].idx

        await omclient.installations.get_by_id(i_id)
        omclient.installation_id = i_id

        await omclient.outputs.get_all()

        await omclient.inputs.get_all()

        await omclient.sensors.get_all()

        await omclient.groupactions.get_all()

        await omclient.thermostats.groups.get_all()

        await omclient.thermostats.units.get_all()

        await omclient.shutters.get_all()

        await omclient.close()


if __name__ == "__main__":
    asyncio.run(main())
