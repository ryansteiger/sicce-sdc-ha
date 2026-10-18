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
        return is_running(self._dev)

    @property
    def percentage(self) -> int:
        return live_power(self._dev)

    async def _send(self, power=None, power_switch=None) -> None:
        await self._client.set_desired_state(self._dev, power=power, power_switch=power_switch)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs) -> None:
        if percentage is not None:
            await self._send(power=percentage, power_switch=True)
        elif live_power(self._dev) == 0 and int(self._dev.get("power") or 0) == 0:
            await self._send(power=50, power_switch=True)
        else:
            await self._send(power_switch=True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._send(power_switch=False)

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage == 0:
            await self._send(power_switch=False)
        else:
            await self._send(power=percentage, power_switch=True)
