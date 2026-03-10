"""Asynchronous Python client for the OpenMotics API."""

from __future__ import annotations

CLOUD_BASE_URL = "https://api.openmotics.com/api"
CLOUD_API_VERSION = "v1.1"

CLOUD_SCOPE = "https://rensonpublic.onmicrosoft.com/eb3ae9c8-806f-4cd5-8b93-737cbf34138d/.default"

CLOUD_API_URL = f"{CLOUD_BASE_URL}/{CLOUD_API_VERSION}"

OAUTH2_AUTHORIZE = "https://rensonpublic.b2clogin.com/rensonpublic.onmicrosoft.com/b2c_1a_smart_hrd_si_r1/oauth2/v2.0/authorize"
OAUTH2_TOKEN = "https://rensonpublic.b2clogin.com/rensonpublic.onmicrosoft.com/b2c_1a_smart_hrd_si_r1/oauth2/v2.0/token"  # nosec

# To be removed in the future
OLD_OAUTH2_TOKEN = f"{CLOUD_API_URL}/authentication/oauth2/token"  # nosec
OLD_OAUTH2_AUTHORIZE = f"{CLOUD_API_URL}/authentication/oauth2/authorize"

#   "configure.outputs configure view.sensors control view.thermostats " \
#   "control.ventilation view.energy configure.thermostats view.outputs " \
#   "view.event_rules control.thermostats view.energy.reports control.outputs" \
#   "view.installations"
OLD_CLOUD_SCOPE = "control view configure"
