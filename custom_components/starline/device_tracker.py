import logging
import re
import json
import subprocess
from collections import namedtuple
from datetime import timedelta
import time

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
    StarlineScanner(hass, config, see)
    return True

class StarlineScanner(object):

    exclude = []

    def __init__(self, hass, config: dict, see):
        self.see = see
        self.hass = hass

        while True:
            self.s = requests.Session() 
            try:
                url = 'https://starline-online.ru/user/login'
                payload = {'LoginForm[login]': config.get(CONF_USERNAME), 'LoginForm[rememberMe]': 'on', 'LoginForm[pass]':config.get(CONF_PASSWORD)}
                response = self.s.post(url, data=payload)
                data = dump.dump_all(response)

                self.success_init = self._update_info() 
                break
            except Exception as e:
                _LOGGER.error("error: "  + str(e))
                time.sleep(5)
                break
       
        track_utc_time_change(
            self.hass, self._update_info, minute=range(0, 60, 5))

    def _update_info(self, now=None):
        url = 'https://starline-online.ru/device'
        payload = {'tz': 180}
   
        response = self.s.get(url, params=payload)
        data = response.json()
        response.close()
        
        for device in data['answer']['devices']:
            x = device['position']['x']
            y = device['position']['y']

            dev_id = device['device_id']

            url = 'https://starline-online.ru/deviceSettings/settings?formId=can&deviceId='+str(dev_id)
            response = self.s.get(url, params=payload)
            can_data = response.json()

            attrs = { }
            
            if 'ctemp' in device:
                attrs.update({'climate_temp': device['ctemp']})

            if 'etemp' in device:
                attrs.update({'engine_temp': device['etemp']})

            if 'battery' in device:
                attrs.update({'battery': device['battery']})

            if 'balance' in device:
                if 'active' in device['balance']:
                    if 'value' in device['balance']['active']:
                        attrs.update({'balance': device['balance']['active']['value']})

            if 'desc' in can_data:
                desc = can_data['desc']
                if 'fuel' in desc:
                    attrs.update({'fuel': desc['fuel']['val']})
                if 'mileage' in desc:
                    attrs.update({'mileage': desc['mileage']['val']})

            if 'car_state' in device:
                states = device['car_state']
                attrs.update({ ("state_"+k): v for k, v in states.items() })
            

            if 'car_alr_state' in device:
                alarm_states = device['car_alr_state']
                attrs.update({ ("alarm_state_"+k): v for k, v in alarm_states.items() })
           
            self.see(
                    dev_id="starline_" + str(dev_id), gps=(y, x), attributes=attrs
                )

        return True