"""Shared entity base for Sicce SDC."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

ALERT_FIELDS = [
    "alert_dry_run",
    "alert_rotor",
    "alert_no_power",
    "alert_temp_high",
    "alert_temp_low",
    "alert_temp_open",
    "alert_temp_short",
    "alert_com",
    "alert_reservoir_low",
    "alert_reservoir_empty",
]


def device_display_name(dev: dict) -> str:
    name = (dev.get("name") or "").strip()
    if name:
        return name
    model = (dev.get("DeviceModel") or {}).get("name") or "Syncra SDC"
    mac = dev.get("mac") or str(dev["id"])
    return f"{model} {mac[-8:]}"


class SicceEntity(CoordinatorEntity):
    def __init__(self, coordinator, client, device_id: int):
        super().__init__(coordinator)
        self._client = client
        self._device_id = device_id

    @property
    def _dev(self) -> dict:
        return self.coordinator.data[self._device_id]

    @property
    def available(self) -> bool:
        dev = self.coordinator.data.get(self._device_id)
        return dev is not None and bool(dev.get("wifi_status"))

    @property
    def device_info(self) -> DeviceInfo:
        dev = self._dev
        model = (dev.get("DeviceModel") or {}).get("name") or "Syncra SDC"
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._device_id))},
            manufacturer="Sicce",
            model=model,
            name=device_display_name(dev),
            sw_version=dev.get("fw_version"),
        )
