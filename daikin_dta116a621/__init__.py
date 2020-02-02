"""The hello_service integration."""
from homeassistant.core import HomeAssistant
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import timedelta
import logging
from pydta116a621 import DaikinAPI
from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

DOMAIN = "daikin_dta116a621"

CONF_ADAPTER_NAME = 'name'
CONF_ADAPTER_HOST = 'host'
CONF_ADAPTER_PORT = 'port'
CONF_ADAPTER_SLAVE = 'slave'
CONF_ADAPTERS = 'adapters'
CONF_ADAPTER = 'adapter'
CONF_INDOOR_UNITS = 'indoor_units'
CONF_INDOOR_UNIT_GLOBAL_NAME = "indoor_unit_global_name"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

PLATFORMS = ["climate"]

ADAPTERS_CONFIG = vol.Schema(
    {
        vol.Required(CONF_ADAPTER_HOST): cv.string,
        vol.Optional(CONF_ADAPTER_NAME, default='default'): cv.string,
        vol.Optional(CONF_ADAPTER_PORT, default=502): cv.port,
        vol.Optional(CONF_ADAPTER_SLAVE, default=1): vol.Clamp(min=1, max=63),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_ADAPTERS, default=[]): vol.All(cv.ensure_list,
                                                                [ADAPTERS_CONFIG]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA
)

async def async_setup(hass: HomeAssistant, config):
    """Establish connection with Daikin."""
    if DOMAIN not in config:
        return True

    conf_adapters = config[DOMAIN].get(CONF_ADAPTERS)
    if not conf_adapters:
        return False

    hass.data.setdefault(DOMAIN, {}).update({CONF_INDOOR_UNITS: {}})

    for conf_adapter in conf_adapters:
        conf_adapter_name = conf_adapter[CONF_ADAPTER_NAME]
        conf_adapter_host = conf_adapter[CONF_ADAPTER_HOST]
        conf_adapter_port = conf_adapter[CONF_ADAPTER_PORT]
        conf_adapter_slave = conf_adapter[CONF_ADAPTER_SLAVE]
        adapter : DaikinAPI = await hass.async_add_executor_job(create_adapter, conf_adapter_host, conf_adapter_port, conf_adapter_slave)

        for indoor_unit in adapter.indoor_units.values():
            indoor_unit_global_name = "daikin_dta116a621_" + conf_adapter_name + "_" + str(indoor_unit.indoor_unit_id).replace("-","_")
            hass.data[DOMAIN][CONF_INDOOR_UNITS][indoor_unit_global_name] = indoor_unit
    hass.helpers.discovery.load_platform('climate', DOMAIN, {}, config)
    #discovery.async_load_platform(hass, DOMAIN, 'climate',  {}, config)
    return True


def create_adapter(host, port, slave) -> DaikinAPI:
    api = DaikinAPI(host, port, slave)
    return api
