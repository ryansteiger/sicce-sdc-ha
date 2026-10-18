"""Config flow for Sicce SDC."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SicceApiError, SicceAuthError, SicceClient
from .const import (
    CONF_EMAIL,
    CONF_MODELS,
    CONF_PASSWORD,
    DOMAIN,
    MODEL_LABELS,
    MODEL_UNKNOWN,
)
from .entity import device_display_name

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class SicceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        return SicceOptionsFlow()

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            client = SicceClient(
                async_get_clientsession(self.hass),
                user_input[CONF_EMAIL],
                user_input[CONF_PASSWORD],
            )
            try:
                await client.login()
                await client.get_devices()
            except SicceAuthError:
                errors["base"] = "invalid_auth"
            except SicceApiError:
                errors["base"] = "cannot_connect"
            if not errors:
                await self.async_set_unique_id(user_input[CONF_EMAIL].lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Sicce SDC (ContrAll)",
                    data=user_input,
                )
        return self.async_show_form(
            step_id="user", data_schema=SCHEMA, errors=errors
        )


class SicceOptionsFlow(config_entries.OptionsFlow):
    """Per-pump model declaration. The Sicce cloud does not report pump
    size, so the user may declare it; it sets the HA model label and
    enables an estimated-flow sensor for that pump."""

    async def async_step_init(self, user_input=None):
        entry = self.config_entry
        data = self.hass.data.get(DOMAIN, {}).get(entry.entry_id)
        devices = (data or {}).get("coordinator").data if data else None
        if not devices:
            return self.async_abort(reason="no_devices")
        current = entry.options.get(CONF_MODELS) or {}
        if user_input is not None:
            models = {
                str(device_id): user_input.get(f"model_{device_id}", MODEL_UNKNOWN)
                for device_id in devices
            }
            return self.async_create_entry(title="", data={CONF_MODELS: models})
        model_options = [{"value": MODEL_UNKNOWN, "label": "Not sure"}] + [
            {"value": key, "label": label} for key, label in MODEL_LABELS.items()
        ]
        schema = {}
        for device_id in sorted(devices):
            schema[
                vol.Optional(
                    f"model_{device_id}",
                    default=current.get(str(device_id), MODEL_UNKNOWN),
                )
            ] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=model_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        listing = "; ".join(
            f"{device_id}: {device_display_name(devices[device_id])}"
            for device_id in sorted(devices)
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            description_placeholders={"devices": listing},
        )
