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
    async_add_entities(
        SicceTempSensor(data["coordinator"], data["client"], device_id)
        for device_id in data["coordinator"].data
    )


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
