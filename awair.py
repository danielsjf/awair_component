"""
Support for the Awair Air Quality Monitor.
For more details about this platform, please refer to the documentation
"""
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_ATTRIBUTION, ATTR_TIME, ATTR_TEMPERATURE, CONF_TOKEN, CONF_MONITORED_CONDITIONS, CONF_NAME)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity

CONF_REFRESH = "refresh_rate"

REQUIREMENTS = ['pyawair==0.0.12']

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = 'Data provided Awair'

# Sensor types are defined like: Name, units
SENSOR_TYPES = { # Aligned with https://developer.getawair.com/console/data-docs
    'score': ['Score', 'Awair Score'],
    'temperature': ['Temperature', '°C'],
    'humidity': ['Humidity', '%'],
    'co2': ['Carbon Dioxide (CO2)', 'ppm'],
    'chemicals': ['Chemicals (TVOCs)', 'ppb'],
    'dust': ['Particulate matter', 'µg/m³'],
    'pm25': ['Particulate matter 2.5', 'µg/m³'],
    'pm10': ['Particulate matter 10', 'µg/m³'],
}

# Sensor types are defined like: Name, Name_API
SENSOR_TYPES_API = {
    'temperature': 'temp',
    'humidity': 'humid',
    'co2': 'co2',
    'chemicals': 'voc',
    'dust': 'dust',
    'pm25': 'pm25',
    'pm10': 'pm10',
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default = list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_REFRESH, default = 60): cv.positive_int,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Awair sensor."""
    from pyawair.auth import AwairAuth
    from pyawair.objects import AwairDev

    _LOGGER.debug("Setting up the Awair platform")

    token = config.get(CONF_TOKEN)
    name = config.get(CONF_NAME)
    refresh_rate = config.get(CONF_REFRESH)
    awair_auth = AwairAuth(token)
    awair_poller = AwairDev(name, awair_auth, refresh_rate)

    devs = []

    for indicator in config[CONF_MONITORED_CONDITIONS]:

        devs.append(AwairSensor(awair_poller, name, indicator))

        _LOGGER.debug("Setting up %s", name)


    add_devices(devs)


class AwairSensor(Entity):
    """Implementation of an Awair sensor."""

    _friendly_name: str

    def __init__(self, awair_poller: object, device_name: str, indicator: str):
        """Initialize the sensor."""
        from pyawair.objects import AwairDev

        self._poller = awair_poller
        self._indicator = indicator
        self._indicator_api = SENSOR_TYPES_API[indicator]
        self._indicator_name = SENSOR_TYPES[indicator][0]
        self._unit = SENSOR_TYPES[indicator][1]
        self._device_name = device_name
        self._friendly_name = '{} - {}'.format(self._device_name,self._indicator_name)

        self._data = self._poller.get_state(self._indicator_api)

        _LOGGER.debug("Initialise %s", self._friendly_name)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._friendly_name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._indicator == 'score':
            return 'mdi:speedometer'
        if self._indicator == 'temperature':
            return 'mdi:thermometer-lines'
        if self._indicator == 'humidity':
            return 'mdi:water-percent'
        if self._indicator == 'co2':
            return 'mdi:periodic-table-co2'
        if self._indicator == 'chemicals':
            return 'mdi:flask-outline'
        if self._indicator == 'dust':
            return 'mdi:factory'
        if self._indicator == 'pm25':
            return 'mdi:factory'
        if self._indicator == 'pm10':
            return 'mdi:factory'

    @property
    def device_class(self):
        """Return the device class."""
        """Icon to use in the frontend, if any."""
        if self._indicator == 'score':
            return None
        if self._indicator == 'temperature':
            return 'temperature'
        if self._indicator == 'humidity':
            return 'humidity'
        if self._indicator == 'co2':
            return 'carbon dioxide'
        if self._indicator == 'chemicals':
            return 'volatile organic compounds'
        if self._indicator == 'dust':
            return 'particulate matter'
        if self._indicator == 'pm25':
            return 'particulate matter 2.5'
        if self._indicator == 'pm10':
            return 'particulate matter 10'

    @property
    def state(self):
        """Return the state of the device."""
        _LOGGER.debug("Get state for %s", self._friendly_name)
        return self._data

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    def update(self):
        """Get the latest data and updates the states."""
        _LOGGER.debug("Update data for %s", self._friendly_name)

        self._data = self._poller.get_state(self._indicator_api)
