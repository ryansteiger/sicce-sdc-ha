"""Minimal async client for the Sicce ThingsCloud API (ContrAll cloud).

Authenticates exactly like the ContrAll app: POST mobile/login with
email/password returns a Bearer token. Commands are desired-state writes:
POST devices/{id}/status with the entire device object, mutating only
`power` (flow %) and `power_switch` (bool).
"""
from __future__ import annotations

import aiohttp

from .const import BASE_URL


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

    async def set_desired_state(self, device_obj: dict, power=None, power_switch=None) -> None:
        """POST the full device object back with power / power_switch mutated."""
        body = dict(device_obj)
        if power is not None:
            body["power"] = int(power)
        if power_switch is not None:
            body["power_switch"] = bool(power_switch)
        data = await self._request("POST", f"devices/{device_obj['id']}/status", body=body)
        if not data.get("result"):
            raise SicceApiError("command not accepted by cloud")

