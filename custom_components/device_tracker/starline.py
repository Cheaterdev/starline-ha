import logging
import re
import json
import subprocess
from collections import namedtuple
from datetime import timedelta

import voluptuous as vol
import requests
import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from homeassistant.util import Throttle
from requests_toolbelt.utils import dump
_LOGGER = logging.getLogger(__name__)
from homeassistant.helpers.event import track_utc_time_change

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})

def setup_scanner(hass, config: dict, see, discovery_info=None):
    """Validate the configuration and return a Starline scanner."""
    StarlineScanner(hass, config, see)
    return True

class StarlineScanner(object):

    exclude = []

    def __init__(self, hass, config: dict, see):
        """Initialize the scanner."""
        self.s = requests.Session() 
        self.see = see
        self.hass = hass
        _LOGGER.debug("Init called")
        
        url = 'https://starline-online.ru/user/login'
        payload = {'LoginForm[login]': config.get(CONF_USERNAME), 'LoginForm[rememberMe]': 'on', 'LoginForm[pass]':config.get(CONF_PASSWORD)}
        response = self.s.post(url, data=payload)

        self.success_init = self._update_info()  
        track_utc_time_change(
            self.hass, self._update_info, minute=range(0, 60, 5))

    def _update_info(self, now=None):
        url = 'https://starline-online.ru/device'
        payload = {'tz': 180}
    
        response = self.s.get(url, params=payload)
        data = response.json()

        for device in data['answer']['devices']:

            x = device['position']['x']
            y = device['position']['y']
            ts = device['position']['ts']

            dev_id = device['device_id']
            attrs = {
    
            }

            self.see(
                    dev_id="starline_" + str(dev_id), gps=(y, x), attributes=attrs
                )
        _LOGGER.debug("Update_info successful")
        return True