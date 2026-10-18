"""Pump control as a fan: percentage = flow %, on/off = power_switch."""
from __future__ import annotations

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SicceEntity, device_display_name, is_running, live_power


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SiccePumpFan(data["coordinator"], data["client"], device_id)
        for device_id in data["coordinator"].data
    )


class SiccePumpFan(SicceEntity, FanEntity):
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_speed_count = 100

    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator, client, device_id)
        self._attr_unique_id = f"sicce_{device_id}_pump"
        self._attr_name = device_display_name(self._dev)

    @property
    def is_on(self) -> bool:
        return self._opt("is_on", is_running(self._dev))

    @property
    def percentage(self) -> int:
        return self._opt("percentage", live_power(self._dev))

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs) -> None:
        if percentage is not None:
            await self._client.apply_flow(self._dev, percentage)
            self._set_optimistic(is_on=True, percentage=int(percentage))
        elif int(self._dev.get("program_v1") or 0) > 0:
            await self._client.set_power_switch(self._dev, True)
            self._set_optimistic(is_on=True, percentage=int(self._dev.get("program_v1") or 0))
        else:
            await self._client.apply_flow(self._dev, 50)
            self._set_optimistic(is_on=True, percentage=50)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._client.set_power_switch(self._dev, False)
        self._set_optimistic(is_on=False, percentage=0)
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        await self._client.apply_flow(self._dev, percentage)
        self._set_optimistic(is_on=int(percentage) > 0, percentage=int(percentage))
        await self.coordinator.async_request_refresh()
