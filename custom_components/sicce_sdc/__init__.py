"""Sicce SDC (ContrAll cloud) integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SicceApiError, SicceAuthError, SicceClient
from .const import CONF_EMAIL, CONF_MODELS, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.BUTTON, Platform.FAN, Platform.NUMBER, Platform.SELECT, Platform.SENSOR, Platform.BINARY_SENSOR]
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = SicceClient(
        async_get_clientsession(hass),
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
    )

    async def _update() -> dict[int, dict]:
        try:
            devices = await client.get_devices()
        except SicceAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except SicceApiError as err:
            raise UpdateFailed(str(err)) from err
        return {int(d["id"]): d for d in devices}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Sicce SDC",
        update_method=_update,
        update_interval=SCAN_INTERVAL,
    )
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryAuthFailed:
        raise
    except Exception as err:  # noqa: BLE001
        raise ConfigEntryNotReady(str(err)) from err

    coordinator.models = dict(entry.options.get(CONF_MODELS) or {})
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
