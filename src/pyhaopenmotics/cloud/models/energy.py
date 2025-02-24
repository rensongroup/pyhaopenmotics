"""Sensor Model for the OpenMotics API."""

from __future__ import annotations

from dataclasses import dataclass

# from dataclasses import field
# from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class EnergySensor(DataClassORJSONMixin):
    """Class holding an OpenMotics Sensor."""

    # Energysensors don't exist in cloud api.
    # This is implemented to keep on par with localgateway

    # pylint: disable=too-many-instance-attributes

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns
        -------
            string

        """
        return ""
