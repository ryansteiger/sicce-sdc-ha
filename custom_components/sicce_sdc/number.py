"""Flow setpoint as a number (0-100 slider) for dashboard-friendly control."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SicceEntity, device_display_name, live_power


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SicceFlowNumber(data["coordinator"], data["client"], device_id)
        for device_id in data["coordinator"].data
    )


class SicceFlowNumber(SicceEntity, NumberEntity):
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:gauge"

    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator, client, device_id)
        self._attr_unique_id = f"sicce_{device_id}_flow"
        self._attr_name = f"{device_display_name(self._dev)} Flow"

    @property
    def native_value(self) -> float:
        return float(live_power(self._dev))

    async def async_set_native_value(self, value: float) -> None:
        await self._client.apply_flow(self._dev, int(value))
        await self.coordinator.async_request_refresh()
