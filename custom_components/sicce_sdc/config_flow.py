"""Config flow for Sicce SDC."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SicceApiError, SicceAuthError, SicceClient
from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class SicceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

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
