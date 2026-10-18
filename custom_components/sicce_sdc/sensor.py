"""Temperature sensor (the pump's real_temp water reading)."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODEL_LABELS, MODEL_MAX_GPH
from .entity import SicceEntity, device_display_name, live_power


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    entities = []
    models = getattr(data["coordinator"], "models", {}) or {}
    for device_id in data["coordinator"].data:
        entities.append(SicceTempSensor(data["coordinator"], data["client"], device_id))
        entities.append(SicceModeSensor(data["coordinator"], data["client"], device_id))
        model_key = models.get(str(device_id))
        if model_key in MODEL_MAX_GPH:
            entities.append(SicceFlowSensor(data["coordinator"], data["client"], device_id, model_key))
    async_add_entities(entities)


class SicceTempSensor(SicceEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator, client, device_id)
        self._attr_unique_id = f"sicce_{device_id}_temperature"
        self._attr_name = f"{device_display_name(self._dev)} Temperature"

    @property
    def native_value(self) -> float | None:
        raw = self._dev.get("real_temp", self._dev.get("temp"))
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None


MODES = {
    1: "Lagoonal Ripple",
    2: "Sharp Break",
    3: "Reef Crest",
    4: "Slow Current",
    5: "Fast Current",
}
PRESETS = {1: "Constant Speed", 2: "Night Mode"}


def mode_label(dev: dict) -> str:
    """Active mode label. A wave mode (mode 1..5) is what the pump is
    actually running whenever one is set, even with preset 1 present in
    the object (verified live: preset=1 + mode=4 runs Slow Current);
    the preset only names the mode when mode is 0."""
    mode = int(dev.get("mode") or 0)
    preset = int(dev.get("preset") or 0)
    if mode in MODES:
        return MODES[mode]
    if preset in PRESETS:
        return PRESETS[preset]
    return "No Mode"


class SicceModeSensor(SicceEntity, SensorEntity):
    _attr_icon = "mdi:waves"

    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator, client, device_id)
        self._attr_unique_id = f"sicce_{device_id}_mode"
        self._attr_name = f"{device_display_name(self._dev)} Mode"

    @property
    def native_value(self) -> str:
        return mode_label(self._dev)

    @property
    def extra_state_attributes(self) -> dict:
        dev = self._dev
        return {
            "mode": dev.get("mode"),
            "preset": dev.get("preset"),
            "sdc3_preset": dev.get("sdc3_preset"),
            "program_status": dev.get("program_status"),
            "eco_mode": dev.get("eco_mode"),
            "pause_mode": dev.get("pause_mode"),
        }


class SicceFlowSensor(SicceEntity, SensorEntity):
    """Estimated flow: live % of the declared model's rated max flow.

    Only created when the user declared a pump model in the options.
    An estimate, not a measurement: real flow depends on head height."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "gph"
    _attr_icon = "mdi:water-pump"

    def __init__(self, coordinator, client, device_id: int, model_key: str):
        super().__init__(coordinator, client, device_id)
        self._model_key = model_key
        self._attr_unique_id = f"sicce_{device_id}_flow_est"
        self._attr_name = f"{device_display_name(self._dev)} Estimated Flow"

    @property
    def native_value(self) -> int:
        return round(live_power(self._dev) * MODEL_MAX_GPH[self._model_key] / 100)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "model": MODEL_LABELS[self._model_key],
            "rated_max_gph": MODEL_MAX_GPH[self._model_key],
            "note": "Estimate from rated max flow at zero head; actual flow depends on plumbing head height.",
        }
