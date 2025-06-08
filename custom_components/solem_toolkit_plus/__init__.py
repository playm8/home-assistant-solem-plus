"""
Home Assistant – Solem Toolkit Plus (parallel fork)
==================================================
A parallel fork of the original Solem Toolkit custom component, with:
    • Better BLE connection stability (retries, back-off)
    • DRY: all helpers factored in a central `SolemClient`
    • Type hints, clearer logs, easier future maintenance

INSTALLATION:
  Place this folder in `custom_components/solem_toolkit_plus/` in your Home Assistant config.
  This version uses domain `solem_toolkit_plus` and can be installed alongside the original toolkit.
  No files from the original toolkit are overwritten.

© 2025 – MIT licence (original authors credited below)
"""
from __future__ import annotations

import asyncio
import logging
import struct
from functools import wraps
from typing import Any, Callable, Dict

from bleak import BleakClient
from homeassistant.core import HomeAssistant, ServiceCall

DOMAIN = "solem_toolkit_plus"
_CHARACTERISTIC_UUID = "108b0002-eab5-bc09-d0ea-0b8f467ce8ee"

# Tweakables — can be overridden via `hass.data[DOMAIN]["options"]` later
DEFAULT_CONNECT_TIMEOUT = 20.0  # seconds
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0  # seconds – doubled at each retry

_LOGGER = logging.getLogger(__name__)

def _retryable(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator providing a simple retry w/ exponential back‑off."""

    @wraps(func)
    async def wrapper(*args, **kwargs):  # type: ignore[override]
        delay = INITIAL_BACKOFF
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return await func(*args, **kwargs)
            except asyncio.CancelledError:
                raise  # let HA shut us down cleanly
            except Exception as exc:  # pylint: disable=broad-except
                if attempt == MAX_RETRIES:
                    _LOGGER.error("Operation %s failed after %s attempts: %s", func.__name__, attempt, exc)
                    raise
                _LOGGER.warning(
                    "Attempt %s/%s for %s failed: %s – retrying in %.1fs",
                    attempt,
                    MAX_RETRIES,
                    func.__name__,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
                delay *= 2

    return wrapper


class SolemClient:
    """Asynchronous BLE wrapper with retries + helper commands."""

    def __init__(self, device_mac: str) -> None:
        self._mac = device_mac

    @_retryable
    async def _send(self, payload: bytes, *, commit: bool = True) -> None:
        async with BleakClient(self._mac, timeout=DEFAULT_CONNECT_TIMEOUT) as client:
            if not client.is_connected:
                raise ConnectionError(f"Unable to connect to {self._mac}")
            await client.write_gatt_char(_CHARACTERISTIC_UUID, payload)
            if commit:
                await client.write_gatt_char(_CHARACTERISTIC_UUID, struct.pack(">BB", 0x3B, 0x00))

    # High‑level helpers ----------------------------------------------------

    async def turn_off_permanent(self) -> None:
        payload = struct.pack(">HBBBH", 0x3105, 0xC0, 0x00, 0x00, 0x0000)
        await self._send(payload)

    async def turn_off_for_days(self, days: int) -> None:
        payload = struct.pack(">HBBBH", 0x3104, 0xC0, days, 0x00, 0x0000)
        await self._send(payload)

    async def turn_on(self) -> None:
        payload = struct.pack(">HBBBH", 0x3106, 0xC0, 0x01, 0x00, 0x0000)
        await self._send(payload)

    async def sprinkle_station(self, station: int, minutes: int) -> None:
        payload = struct.pack(">HBBBH", 0x3401, station, minutes, 0x00, 0x0000)
        await self._send(payload)

    async def sprinkle_all(self, minutes: int) -> None:
        payload = struct.pack(">HBBBH", 0x3400, 0x00, minutes, 0x00, 0x0000)
        await self._send(payload)

    async def run_program(self, program: int) -> None:
        # 0x3200 == programme 0, 0x3201 == programme 1, etc.
        payload = struct.pack(">HBBBH", 0x3200 + program, 0x00, 0x00, 0x00, 0x0000)
        await self._send(payload)

    async def stop_manual(self) -> None:
        payload = struct.pack(">HBBBH", 0x3009, 0x00, 0x00, 0x00, 0x0000)
        await self._send(payload)


# -------------------------- HA glue layer ------------------------------- #

async def async_setup(hass: HomeAssistant, config: Dict[str, Any]):
    """Bare‑bones setup – all the magic lives in service handlers."""
    _async_setup_services(hass)
    return True


def _async_setup_services(hass: HomeAssistant) -> None:
    async def _dispatch(call: ServiceCall, action: str):
        device_mac: str = call.data["device_mac"]
        client = SolemClient(device_mac)
        try:
            if action == "turn_off_permanent":
                await client.turn_off_permanent()
            elif action == "turn_off_x_days":
                await client.turn_off_for_days(call.data["days"])
            elif action == "turn_on":
                await client.turn_on()
            elif action == "sprinkle_station":
                await client.sprinkle_station(call.data["station"], call.data["minutes"])
            elif action == "sprinkle_all":
                await client.sprinkle_all(call.data["minutes"])
            elif action == "run_program":
                await client.run_program(call.data["program"])
            elif action == "stop_manual":
                await client.stop_manual()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Solem action %s failed", action)
            raise  # let HA show a service call failure

    # Map "service → action key"
    service_map = {
        "turn_off_permanent": "turn_off_permanent",
        "turn_off_x_days": "turn_off_x_days",
        "turn_on": "turn_on",
        "sprinkle_station": "sprinkle_station",
        "sprinkle_all": "sprinkle_all",
        "run_program": "run_program",
        "stop_manual": "stop_manual",
    }

    for service_name, action_key in service_map.items():
        hass.services.async_register(
            DOMAIN,
            service_name,
            lambda call, ak=action_key: _dispatch(call, ak),  # default‑arg trick to bind action_key
        )

    _LOGGER.info("%s services registered: %s", DOMAIN, ", ".join(service_map))
