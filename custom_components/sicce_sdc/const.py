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
