from homeassistant.core import HomeAssistant
from homeassistant.components.climate import ClimateDevice
from homeassistant.const import ATTR_TEMPERATURE, CONF_HOST, CONF_NAME, TEMP_CELSIUS
from homeassistant.components.climate import SUPPORT_FAN_MODE, SUPPORT_TARGET_TEMPERATURE
from homeassistant.components.climate.const import HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_HEAT_COOL, \
    HVAC_MODE_AUTO, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY, SUPPORT_TARGET_TEMPERATURE_RANGE
from homeassistant.util.temperature import convert as convert_temperature

from pydta116a621 import IndoorUnit
from pydta116a621.const import (CONST_HVAC_POWER_OFF, CONST_HVAC_POWER_ON,
                                )
from . import DOMAIN as DAIKIN_DOMAIN, CONF_INDOOR_UNIT_GLOBAL_NAME, CONF_INDOOR_UNITS

def setup_platform(hass : HomeAssistant, config, add_devices, discovery_info=None):
    devices = []
    for name, unit in hass.data[DAIKIN_DOMAIN][CONF_INDOOR_UNITS].items():
        devices.append(DTA116A62Climate(unit, name))
    add_devices(devices)

class DTA116A62Climate(ClimateDevice):
    def __init__(self, api: IndoorUnit, name):
        """Initialize the climate device."""
        self._api= api
        self._name = name

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FAN_MODE | SUPPORT_TARGET_TEMPERATURE

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this thermostat uses."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._api.real_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._api.target_temperature

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 0.1


    @property
    def min_temp(self) -> float:
        mint, _ = self._api.supported_cool_temperature
        if(self.hvac_mode == HVAC_MODE_HEAT):
            min_temp, max_temp = self._api.supported_heat_temperature
        return convert_temperature(
            mint, TEMP_CELSIUS, self.temperature_unit
        )

    @property
    def max_temp(self) -> float:
        _, maxt = self._api.supported_cool_temperature
        if(self.hvac_mode == HVAC_MODE_HEAT):
            min_temp, max_temp = self._api.supported_heat_temperature
        """Return the maximum temperature."""
        return convert_temperature(
            maxt, TEMP_CELSIUS, self.temperature_unit
        )

    def set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        self._api.write_target_temperature(temperature)

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        if(self._api.hvac_power == CONST_HVAC_POWER_OFF):
            return HVAC_MODE_OFF
        else:
            return self._api.hvac_mode

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        modes = self._api.supported_hvac_modes
        return list(modes + [HVAC_MODE_OFF])

    def set_hvac_mode(self, hvac_mode):
        if(hvac_mode == HVAC_MODE_OFF):
            self._api.write_hvac_power(CONST_HVAC_POWER_OFF)
        else:
            self._api.write_hvac_power(CONST_HVAC_POWER_ON)
            self._api.write_hvac_mode(hvac_mode)
    @property
    def fan_mode(self):
        """Return the fan setting."""
        return self._api.fan_mode

    @property
    def fan_modes(self):
        """List of available fan modes."""
        return self._api.supported_fan_modes

    def set_fan_mode(self, fan_mode):
        """Set new target temperature."""
        self._api.write_fan_mode(fan_mode)

    def turn_on(self):
        self._api.write_hvac_power(CONST_HVAC_POWER_ON)

    @property
    def swing_mode(self):
        """Return the fan setting."""
        return self._api.swing_mode

    def set_swing_mode(self, swing_mode):
        """Set new target temperature."""
        self._api.write_swing_mode(swing_mode)

    @property
    def swing_modes(self):
        """List of available swing modes."""
        return self._api.supported_swing_modes

    def update(self):
        """Retrieve latest state."""
        self._api.update_all()




