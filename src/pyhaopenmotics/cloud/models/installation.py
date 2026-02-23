"""Installation Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class Allowed(DataClassORJSONMixin):
    """Object holding an OpenMotics Installation."""

    allowed: bool | None = field(default=None)


@dataclass
class Acl(DataClassORJSONMixin):
    """Object holding an OpenMotics Installation."""

    configure: Allowed | None = field(default=None)
    view: Allowed | None = field(default=None)
    control: Allowed | None = field(default=None)


@dataclass
class Network(DataClassORJSONMixin):
    """Object holding an OpenMotics Installation."""

    local_ip_address: str | None = field(default=None)


@dataclass
class Installation(DataClassORJSONMixin):
    """Object holding an OpenMotics Installation.

    # noqa: E800
    # {
    #     'id': 1,
    #     'name': 'John Doe',
    #     'description': '',
    #     'gateway_model': 'openmotics',
    #     '_acl': {'configure': {'allowed': True}, 'view': {'allowed': True},
    #             'control': {'allowed': True}},
    #     '_version': 1.0, 'user_role': {'role': 'ADMIN', 'user_id': 1},
    #     'registration_key': 'xxxxx-xxxxx-xxxxxxx',
    #     'platform': 'CLASSIC',
    #     'building_roles': [],
    #     'version': '1.16.5',
    #     'network': {'local_ip_address': '172.16.1.25'},
    #     'flags': {'UNREAD_NOTIFICATIONS': 0, 'ONLINE': None},
    #     'features':
    #         ["control_events",
    #           "dirty_flag",
    #           "100_steps_dimmer",
    #           "measurement_counter_schema",
    #           "in_use_property",
    #           "websocket_maintenance",
    #           "modules_information",
    #           "thermostat_groups",
    #           "hot_water_schema",
    #           "default_timer_disabled",
    #           "cloud_event_logs",
    #           "isolated_plugins",
    #           "input_states",
    #           "sensors_exclude_source",
    #           "sensor_parameter",
    #           "current_transformer_schema",
    #           "sync_modules_information",
    #           "show_in_app_property",
    #           "metrics",
    #           "dynamic_updates",
    #           "shutter_positions",
    #           "thermostat_v1",
    #           "ventilation_schema",
    #           "network_discovery",
    #           "long_names",
    #           "pause_schedules",
    #           "thermostats_gateway",
    #           "scheduling",
    #           "gateway_sensors",
    #           "factory_reset"
    #           "gateway_maintenance",]
    # }
    """

    # pylint: disable=too-many-instance-attributes
    name: str
    idx: int = field(metadata=field_options(alias="id"))
    description: str | None = field(default=None)
    gateway_model: str | None = field(default=None)
    acl: Acl | None = field(
        default=None,
        metadata=field_options(alias="_acl"),
    )
    version: str | None = field(
        default=None,
        metadata=field_options(alias="_version"),
    )

    user_role: dict[str, Any] | None = field(default=None)
    registration_key: str | None = field(default=None)
    platform: str | None = field(default=None)
    building_roles: list | None = field(default=None)
    network: Network | None = field(default=None)
    flags: dict[str, Any] | None = field(default=None)
    features: list | None = field(default=None)

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return f"{self.idx}_{self.name}"
