"""Flow setpoint as a number (0-100 slider) for dashboard-friendly control."""
from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SicceEntity, device_display_name, live_power


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id in data["coordinator"].data:
        entities.append(SicceFlowNumber(data["coordinator"], data["client"], device_id))
        entities.append(SicceTempThresholdNumber(data["coordinator"], data["client"], device_id, "low"))
        entities.append(SicceTempThresholdNumber(data["coordinator"], data["client"], device_id, "high"))
    async_add_entities(entities)


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
        return self._opt("value", float(live_power(self._dev)))

    async def async_set_native_value(self, value: float) -> None:
        await self._client.apply_flow(self._dev, int(value))
        self._set_optimistic(value=float(int(value)), is_on=int(value) > 0)
        await self.coordinator.async_request_refresh()


class SicceTempThresholdNumber(SicceEntity, NumberEntity):
    """Temperature alert threshold from the pump's alarm settings.

    Native values are deg C; Home Assistant displays them in the
    system unit (deg F for most US installs)."""

    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = 0
    _attr_native_max_value = 50
    _attr_native_step = 0.1
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, client, device_id: int, which: str):
        super().__init__(coordinator, client, device_id)
        self._field = "low_temp_th" if which == "low" else "high_temp_th"
        self._attr_icon = "mdi:thermometer-low" if which == "low" else "mdi:thermometer-high"
        self._attr_unique_id = f"sicce_{device_id}_temp_{which}"
        label = "Temp Alert Low" if which == "low" else "Temp Alert High"
        self._attr_name = f"{device_display_name(self._dev)} {label}"

    @property
    def native_value(self) -> float | None:
        raw = self._dev.get(self._field)
        if raw is None:
            return None
        return self._opt("value", float(raw))

    async def async_set_native_value(self, value: float) -> None:
        dev = self._dev
        low = float(value) if self._field == "low_temp_th" else float(dev.get("low_temp_th") or 0)
        high = float(value) if self._field == "high_temp_th" else float(dev.get("high_temp_th") or 0)
        await self._client.set_temp_thresholds(dev, low, high)
        self._set_optimistic(value=float(value))
        await self.coordinator.async_request_refresh()
