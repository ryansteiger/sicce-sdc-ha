"""Shared entity base for Sicce SDC."""
from __future__ import annotations

import time

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODEL_LABELS

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
        self._optimistic_until = 0.0
        self._optimistic_values: dict = {}

    def _set_optimistic(self, **values) -> None:
        """Hold commanded values until the pump's own status report
        confirms them. The pump takes ~10 s to report a change back to
        the cloud; without this, HA repaints the stale state over the
        user's action (the toggle visibly bounces back)."""
        self._optimistic_values.update(values)
        self._optimistic_until = time.monotonic() + 45

    def _opt(self, key, live):
        """Optimistic value while pending, live value once the pump
        reports it (or the hold expires)."""
        if key in self._optimistic_values:
            if live == self._optimistic_values[key]:
                del self._optimistic_values[key]
                return live
            if time.monotonic() < self._optimistic_until:
                return self._optimistic_values[key]
            del self._optimistic_values[key]
        return live

    @property
    def _dev(self) -> dict:
        return self.coordinator.data[self._device_id]

    @property
    def available(self) -> bool:
        dev = self.coordinator.data.get(self._device_id)
        return dev is not None and bool(dev.get("wifi_status"))

    @property
    def model_key(self) -> str | None:
        """User-declared pump model key from the integration options."""
        models = getattr(self.coordinator, "models", {}) or {}
        key = models.get(str(self._device_id))
        return key if key in MODEL_LABELS else None

    @property
    def device_info(self) -> DeviceInfo:
        dev = self._dev
        model = MODEL_LABELS.get(self.model_key) or (dev.get("DeviceModel") or {}).get("name") or "Syncra SDC"
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._device_id))},
            manufacturer="Sicce",
            model=model,
            name=device_display_name(dev),
            sw_version=dev.get("fw_version"),
        )


def _mb(dev: dict) -> list:
    mb = dev.get("mb_status")
    return mb if isinstance(mb, list) else []


def live_power(dev: dict) -> int:
    """Actual current flow % from the mainboard status registers.

    The top-level `power` field is the app's last-posted setpoint and sits
    at 0 when the pump was set from its physical dial. mb_status[5] is the
    live output (verified: 74 on a pump running 74%, 0 on a stopped pump
    whose setpoint register mb_program[2] still reads 50).
    """
    mb = _mb(dev)
    if len(mb) > 5:
        try:
            return int(mb[5])
        except (TypeError, ValueError):
            pass
    return int(dev.get("power") or 0)


def is_running(dev: dict) -> bool:
    """mb_status[0] is the running flag (1 running, 0 stopped)."""
    mb = _mb(dev)
    if len(mb) > 0:
        return int(mb[0] or 0) == 1
    return bool(dev.get("power_switch"))
