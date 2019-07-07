# NEW: Starline integration through official API:
https://github.com/Cheaterdev/starline_api-ha
----------------------------
# starline-ha
Starline device tracker for Home Assistant

## Features
Exposes all your Starline devices with GPS coordinates.

## Setup

```yaml
# configuration.yaml

device_tracker:
  - platform: starline
    scan_interval: 00:02:00
    username: !USERNAME!
    password: !PASSWORD!
```

Configuration variables:
- **username** (*Required*): Your Starline username
- **password** (*Required*): Your Starline password
- **scan_interval** (*Optional*): Time to refresh data

# Device naming
 - starline_**IMEI**
