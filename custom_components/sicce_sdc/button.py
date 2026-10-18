"""Feed mode button: starts or ends a feed pause, like the app."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SicceEntity, device_display_name


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SicceFeedButton(data["coordinator"], data["client"], device_id)
        for device_id in data["coordinator"].data
    )


class SicceFeedButton(SicceEntity, ButtonEntity):
    _attr_icon = "mdi:fish"

    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator, client, device_id)
        self._attr_unique_id = f"sicce_{device_id}_feed_button"
        self._attr_name = f"{device_display_name(self._dev)} Feed Mode"

    async def async_press(self) -> None:
        await self._client.set_pause(self._dev, not bool(self._dev.get("pause_mode")))
        await self.coordinator.async_request_refresh()
