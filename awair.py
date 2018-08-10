"""
Support for the Awair Air Quality Monitor.
For more details about this platform, please refer to the documentation
"""
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_ATTRIBUTION, ATTR_TIME, ATTR_TEMPERATURE, CONF_TOKEN, CONF_MONITORED_CONDITIONS, CONF_NAME, CONF_SCAN_INTERVAL)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity

REQUIREMENTS = ['pyawair==0.0.4']

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = 'Data provided Awair'

# Sensor types are defined like: Name, units
SENSOR_TYPES = {
    'score': ['Score', 'Awair Score'],
    'temperature': ['Temperature', '°C'],
    'humidity': ['Humidity', '%'],
    'co2': ['CO2', 'ppm of CO2'],
    'chemicals': ['Chemicals', 'ppb of chemicals'],
    'dust': ['Dust', 'µg/m³ of dust'],
}

# Sensor types are defined like: Name, Name_API
SENSOR_TYPES_API = {
    'temperature': 'temp',
    'humidity': 'humid',
    'co2': 'co2',
    'chemicals': 'voc',
    'dust': 'dust',
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default = list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_SCAN_INTERVAL, default = 60): cv.NUMERIC_STATE_CONDITION_SCHEMA,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Awair sensor."""
    from pyawair.auth import AwairAuth

    token = config.get(CONF_TOKEN)
    name = config.get(CONF_NAME)
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    awair_auth = AwairAuth(token)

    devs = []

    for indicator in config[CONF_MONITORED_CONDITIONS]:
        devs.append(AwairSensor(
            awair_auth, token, name, indicator, scan_interval))

    add_devices(devs)


class AwairSensor(Entity):
    """Implementation of an Awair sensor."""
    _friendly_name: str

    def __init__(self, awair_auth, token, device_name, indicator, scan_interval):
        """Initialize the sensor."""
        from pyawair.data import get_all_devices

        self._token = token
        self._auth = awair_auth
        self._device_name = device_name
        self._indicator = indicator
        self._indicator_name = SENSOR_TYPES[indicator][0]
        self._unit = SENSOR_TYPES[indicator][1]
        self._friendly_name = '{} {}'.format(self._device_name,self._indicator_name)
        self._scan_interval = scan_interval
        devices = get_all_devices(awair_auth)
        self._type = next((item for item in devices if item["name"] == device_name),
                          False)['deviceType']  # get the device type
        self._id = next((item for item in devices if item["name"] == device_name),
                        False)['deviceId']  # get the device ID

        self._data = None

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

    @property
    def state(self):
        """Return the state of the device."""
        if self._data is not None:
            return self._data
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    def update(self):
        """Get the latest data and updates the states."""
        from pyawair.data import get_current_air_data

        _LOGGER.debug("Update data for %s", self._friendly_name)

        result = get_current_air_data(self._auth, device_type=self._type,device_id=self._id)
        data = None

        if self._indicator == 'score':
            data = result[0]['score']
        else:
            data = next((item for item in result[0]['sensors'] if item["comp"] == SENSOR_TYPES_API[self._indicator]), False)['value']

        self._data = data