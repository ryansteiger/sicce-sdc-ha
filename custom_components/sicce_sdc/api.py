"""Minimal async client for the Sicce ThingsCloud API (ContrAll cloud).

Authenticates exactly like the ContrAll app: POST mobile/login with
email/password returns a Bearer token. Commands go to the SDC 3.0
controller's program endpoint, POST devices/{id}/v2/program (the same
endpoint DeviceControllerSDC3.updateDevice uses): a one-field
{"power_switch": bool} body for on/off, or a program body
{program, mode, v1, v2, t1, t2, start, program_preset} for speed/mode.
Verified live 2026-10-18. (POST devices/{id}/status accepts writes but
the pump ignores them; it is the older controller's path.)
"""
from __future__ import annotations

import aiohttp

from .const import BASE_URL, COLOR_LED_PCT


class SicceApiError(Exception):
    """Generic API failure."""


class SicceAuthError(SicceApiError):
    """Login rejected or token refused."""


class SicceClient:
    def __init__(self, session: aiohttp.ClientSession, email: str, password: str):
        self._session = session
        self._email = email
        self._password = password
        self._token: str | None = None

    async def login(self) -> None:
        try:
            async with self._session.post(
                BASE_URL + "mobile/login",
                json={"email": self._email, "password": self._password},
            ) as resp:
                data = await resp.json(content_type=None)
                if resp.status != 200 or not data.get("result") or not data.get("token"):
                    raise SicceAuthError(f"login failed: HTTP {resp.status}")
                self._token = data["token"]
        except aiohttp.ClientError as err:
            raise SicceApiError(str(err)) from err

    async def _request(self, method: str, path: str, body=None, retry: bool = True):
        if self._token is None:
            await self.login()
        headers = {"Authorization": f"Bearer {self._token}"}
        try:
            async with self._session.request(
                method, BASE_URL + path, json=body, headers=headers
            ) as resp:
                if resp.status == 401 and retry:
                    self._token = None
                    await self.login()
                    return await self._request(method, path, body, retry=False)
                data = await resp.json(content_type=None)
                if resp.status != 200:
                    raise SicceApiError(f"{method} {path}: HTTP {resp.status}")
                return data
        except aiohttp.ClientError as err:
            raise SicceApiError(str(err)) from err

    async def get_devices(self) -> list[dict]:
        data = await self._request("GET", "devices")
        return data.get("data") or []

    async def get_device(self, device_id: int) -> dict:
        data = await self._request("GET", f"devices/{device_id}")
        return data["data"]

    async def _post_program(self, device_id: int, body: dict) -> None:
        data = await self._request("POST", f"devices/{device_id}/v2/program", body=body)
        if not data.get("result"):
            raise SicceApiError("command not accepted by cloud")

    async def set_power_switch(self, device_obj: dict, on: bool) -> None:
        """On/off: one-field body to the program endpoint, as the app sends."""
        await self._post_program(device_obj["id"], {"power_switch": bool(on)})

    async def set_program(self, device_obj: dict, v1=None, mode=None, program=None) -> None:
        """Speed/mode write built from the device's current program fields.
        v1 is the primary speed %. t1/t2 are sent in tenths, as stored."""
        body = {
            "program_preset": int(device_obj.get("program_preset") or 0),
            "program": int(program if program is not None else (device_obj.get("preset") or 1)),
            "mode": int(mode if mode is not None else (device_obj.get("mode") or 0)),
            "v1": int(v1 if v1 is not None else (device_obj.get("program_v1") or 0)),
            "v2": int(device_obj.get("program_v2") or 0),
            "t1": (device_obj.get("program_t1") or 0) / 10,
            "t2": (device_obj.get("program_t2") or 0) / 10,
            "start": 0,
        }
        await self._post_program(device_obj["id"], body)

    def _settings_body(self, device_obj: dict, **overrides) -> dict:
        """The /v2/settings body the app assembles, with overrides."""
        body = {
            "slave_ids": device_obj.get("slave_ids") or [],
            "counterphase": device_obj.get("master_slave_phase") or 0,
            "color_id": device_obj.get("device_color_id"),
            "name": device_obj.get("name"),
            "aquarium_id": device_obj.get("aquarium_id"),
            "low_temp_th": device_obj.get("low_temp_th"),
            "high_temp_th": device_obj.get("high_temp_th"),
            "led_r": device_obj.get("led_r"),
            "led_g": device_obj.get("led_g"),
            "led_b": device_obj.get("led_b"),
        }
        body.update(overrides)
        return body

    async def _post_settings(self, device_obj: dict, **overrides) -> None:
        data = await self._request(
            "POST",
            f"devices/{device_obj['id']}/v2/settings",
            body=self._settings_body(device_obj, **overrides),
        )
        if not data.get("result"):
            raise SicceApiError("settings change not accepted by cloud")

    async def set_color(self, device_obj: dict, color_id: int) -> None:
        """Pump color: POST devices/{id}/v2/settings with the settings
        body the app assembles. color_id sets the app icon; the led_*
        percentages (the palette color converted from its hex) drive
        the controller's ring LED, which the pump adopts from the
        settings record and then reports back. Verified live on a
        bench unit 2026-10-18 (green -> purple, seen on the hardware).
        """
        led = COLOR_LED_PCT[int(color_id)]
        await self._post_settings(
            device_obj,
            color_id=int(color_id),
            led_r=led[0],
            led_g=led[1],
            led_b=led[2],
        )

    async def set_temp_thresholds(
        self, device_obj: dict, low_c: float, high_c: float
    ) -> None:
        """Temperature alert thresholds (deg C), the app's alarm
        settings. Verified live 2026-10-18 on a bench unit."""
        await self._post_settings(
            device_obj, low_temp_th=float(low_c), high_temp_th=float(high_c)
        )

    async def apply_flow(self, device_obj: dict, pct: int) -> None:
        """Set flow %: 0 turns the pump off; >0 switches it on if needed,
        then writes the speed as the program's v1."""
        pct = int(pct)
        if pct <= 0:
            await self.set_power_switch(device_obj, False)
            return
        if not device_obj.get("power_switch"):
            await self.set_power_switch(device_obj, True)
        await self.set_program(device_obj, v1=pct)

