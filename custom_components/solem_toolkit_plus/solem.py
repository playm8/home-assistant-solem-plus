"""
Minimal synchronous BLE client for Solem sprinklers.

Only the calls used by coordinator.py / switch.py are implemented.
Runs inside Home Assistant's executor thread, so all I/O is blocking here.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from bleak import BleakClient

_LOGGER = logging.getLogger(__name__)

# Replace these UUIDs once you've scanned your device with nRF Connect.
STATE_CHAR = "a003"
CONTROL_CHAR = "a003"          # some firmware uses the same characteristic
BATTERY_CHAR = "2a19"


class SolemClient:
    """Blocking BLE helper used by the data-update coordinator."""

    def __init__(self, mac: str) -> None:
        self._mac = mac
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._client: BleakClient | None = None

    # ───────────────────────────── public API
    def get_status(self) -> dict[str, int | bool]:
        """Return {'battery': int, 'is_watering': bool}."""
        client = self._ensure_connected()
        battery = int(self._run(client.read_gatt_char(BATTERY_CHAR))[0])
        watering = bool(self._run(client.read_gatt_char(STATE_CHAR))[0])
        return {"battery": battery, "is_watering": watering}

    def start_watering(self) -> None:
        self._write_control(True)

    def stop_watering(self) -> None:
        self._write_control(False)

    # ───────────────────────────── helpers
    def _write_control(self, on: bool) -> None:
        payload = bytes([0x01 if on else 0x00])
        self._run(self._ensure_connected().write_gatt_char(CONTROL_CHAR, payload))

    def _ensure_connected(self) -> BleakClient:
        """Connect if necessary and return the active BleakClient."""
        if self._client and self._client.is_connected:
            return self._client

        self._client = BleakClient(self._mac, loop=self._loop)
        self._run(self._client.connect(timeout=10))
        _LOGGER.debug("Connected to %s", self._mac)
        return self._client

    def _run(self, coro):
        """Run *coro* inside the private event loop and return its result."""
        return self._loop.run_until_complete(coro)

    def __del__(self):
        with suppress(Exception):
            if self._client and self._client.is_connected:
                self._run(self._client.disconnect())
