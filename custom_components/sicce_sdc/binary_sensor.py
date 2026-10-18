"""Problem binary sensor: on when any device alert flag is raised."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ALERT_FIELDS, SicceEntity, active_alerts, device_display_name


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SicceProblemSensor(data["coordinator"], data["client"], device_id)
        for device_id in data["coordinator"].data
    )


class SicceProblemSensor(SicceEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator, client, device_id)
        self._attr_unique_id = f"sicce_{device_id}_problem"
        self._attr_name = f"{device_display_name(self._dev)} Problem"

    @property
    def is_on(self) -> bool:
        return any(bool(self._dev.get(f)) for f in ALERT_FIELDS)

    @property
    def extra_state_attributes(self) -> dict:
        dev = self._dev
        attrs = {f: bool(dev.get(f)) for f in ALERT_FIELDS}
        attrs["active_alerts"] = active_alerts(dev)
        attrs["com_error_count"] = dev.get("com_error_count")
        attrs["last_status_update"] = dev.get("last_status_update")
        attrs["wifi_status"] = dev.get("wifi_status")
        return attrs
