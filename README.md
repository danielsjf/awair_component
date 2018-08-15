# Awair platform for Home assistant
[Home Assistant](https://www.home-assistant.io/) platform for the [Awair](https://getawair.com/) air quality monitor.

This project uses the Awair API which is currently still in beta. Access can be requested via the Awair [developer console](https://developer.getawair.com).

This platform extends the sensor component. To enable this platform, create a new file with the contents of `awair.py` in `<config>/custom_components/sensor/awair.py`.

Next, add the following lines to your `configuration.yaml`:

```yaml
sensor:
  - platform: awair
    token: SECRET
    name: Your sensor name
    monitored_conditions:
      - temperature
      - humidity
      - co2
      - chemicals
      - dust
    refresh_rate: 15 # minutes between polling; default is 60; max API calls per day currently 100
```

The token can be found via the [Awair developer console](https://developer.getawair.com/console/personal).

The custom component uses the [pyawair package](https://pypi.org/project/pyawair/) that can be found on pypi.

# Warning
This component is still under active development, as are the Awair API and the pyawair package. Please understand that these are all still in beta and functionality might change.
