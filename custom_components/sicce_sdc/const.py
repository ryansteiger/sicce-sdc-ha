DOMAIN = "sicce_sdc"
BASE_URL = "https://sicce.thingscloud.it/api/"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# The cloud API does not expose pump size: every size reports the same
# platform DeviceModel ("Syncra SDC 3.0", id 9). Users may optionally
# declare the model per pump in the integration options. The declaration
# drives the HA model label and an estimated-flow sensor.
# Rated max flow at zero head, in GPH (manufacturer specs, approximate).
MODEL_UNKNOWN = "unknown"
MODEL_LABELS = {
    "sdc_3_0": "Syncra SDC 3.0",
    "sdc_6_0": "Syncra SDC 6.0",
    "sdc_9_0": "Syncra SDC 9.0",
}
MODEL_MAX_GPH = {"sdc_3_0": 800, "sdc_6_0": 1450, "sdc_9_0": 2500}
CONF_MODELS = "models"

# Pump icon color catalog, from GET /api/colors. The id is written via
# /v2/settings as color_id; codes are the API's, labels are for display.
COLOR_IDS = {
    "Yellow": 1,
    "Orange": 2,
    "Red": 3,
    "Purple": 4,
    "Green": 5,
    "Blue": 6,
    "Dark Blue": 7,
}
COLOR_LABEL_BY_CODE = {
    "yellow": "Yellow",
    "orange": "Orange",
    "red": "Red",
    "purple": "Purple",
    "green": "Green",
    "blue": "Blue",
    "darkblue": "Dark Blue",
}

# Palette hex values from GET /api/colors; the device drives its ring
# LED from the led_r/g/b percentages in the /v2/settings record, so a
# color write sends the palette hex converted to percentages.
COLOR_HEX_BY_ID = {
    1: "9EA648",
    2: "C67C51",
    3: "9C4A6A",
    4: "8360BB",
    5: "B2DF89",
    6: "4EB1E3",
    7: "2C79CE",
}
