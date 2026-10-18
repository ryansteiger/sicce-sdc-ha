"""Operating mode as a select (Constant, Night, and the wave modes).

Write path verified live on a bench unit 2026-10-18 via
POST devices/{id}/v2/program: program=1 + mode=0 is Constant Speed,
program=2 is Night Mode, program=1 + mode 1..5 are the wave modes.
"""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COLOR_IDS, COLOR_LABEL_BY_CODE, DOMAIN
from .entity import SicceEntity, device_display_name
from .sensor import MODES, mode_label

# label -> (program, mode)
MODE_OPTIONS: dict[str, tuple[int, int]] = {
    "Constant Speed": (1, 0),
    "Night Mode": (2, 0),
    **{label: (1, value) for value, label in MODES.items()},
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id in data["coordinator"].data:
        entities.append(SicceModeSelect(data["coordinator"], data["client"], device_id))
        entities.append(SicceColorSelect(data["coordinator"], data["client"], device_id))
    async_add_entities(entities)


class SicceModeSelect(SicceEntity, SelectEntity):
    _attr_icon = "mdi:waves"
    _attr_options = list(MODE_OPTIONS)

    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator, client, device_id)
        self._attr_unique_id = f"sicce_{device_id}_mode_select"
        self._attr_name = f"{device_display_name(self._dev)} Mode Control"

    @property
    def current_option(self) -> str | None:
        label = mode_label(self._dev)
        live = label if label in MODE_OPTIONS else None
        return self._opt("option", live)

    async def async_select_option(self, option: str) -> None:
        program, mode = MODE_OPTIONS[option]
        await self._client.set_program(self._dev, program=program, mode=mode)
        self._set_optimistic(option=option)
        await self.coordinator.async_request_refresh()


class SicceColorSelect(SicceEntity, SelectEntity):
    """Pump color, the app's palette (GET /api/colors): sets both the
    app icon color and the controller ring LED."""

    _attr_icon = "mdi:palette"
    _attr_options = list(COLOR_IDS)

    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator, client, device_id)
        self._attr_unique_id = f"sicce_{device_id}_color"
        self._attr_name = f"{device_display_name(self._dev)} Pump Color"

    @property
    def current_option(self) -> str | None:
        code = (self._dev.get("DeviceColor") or {}).get("code")
        if code in COLOR_LABEL_BY_CODE:
            return COLOR_LABEL_BY_CODE[code]
        color_id = self._dev.get("device_color_id")
        for label, cid in COLOR_IDS.items():
            if cid == color_id:
                return label
        return None

    async def async_select_option(self, option: str) -> None:
        await self._client.set_color(self._dev, COLOR_IDS[option])
        await self.coordinator.async_request_refresh()
