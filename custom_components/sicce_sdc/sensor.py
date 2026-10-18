"""Temperature sensor (the pump's real_temp water reading)."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SicceEntity, device_display_name


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id in data["coordinator"].data:
        entities.append(SicceTempSensor(data["coordinator"], data["client"], device_id))
        entities.append(SicceModeSensor(data["coordinator"], data["client"], device_id))
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
    mode = int(dev.get("mode") or 0)
    preset = int(dev.get("preset") or 0)
    if dev.get("program_status") and mode in MODES:
        return MODES[mode]
    if preset in PRESETS:
        return PRESETS[preset]
    if mode in MODES:
        return MODES[mode]
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
