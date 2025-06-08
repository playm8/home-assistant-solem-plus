"""Config flow for Solem Toolkit Plus."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_MAC
from homeassistant.components.bluetooth import (
    BluetoothServiceInfo,
    async_discovered_service_info,
)

from .const import DOMAIN

COMPANY_ID_SOLEM = 0x079E  # Bluetooth SIG company identifier for SOLEM (1950 decimal)


class SolemConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Solem Toolkit Plus."""

    VERSION = 1

    # ──────────────────────────────────────────────────────────────
    # Manual setup step (user enters MAC address)
    # ──────────────────────────────────────────────────────────────
    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            mac = user_input[CONF_MAC]
            await self.async_set_unique_id(mac)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=mac, data={"device_mac": mac})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_MAC): str}),
            errors=errors,
        )

    # ──────────────────────────────────────────────────────────────
    # Automatic Bluetooth discovery (advertisements with SOLEM company ID)
    # ──────────────────────────────────────────────────────────────
    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfo
    ):
        """Called automatically by HA’s BLE scanner when a matching packet is seen."""
        # Safety check: ignore other manufacturers
        if discovery_info.manufacturer_id != COMPANY_ID_SOLEM:
            return self.async_abort(reason="not_solem")

        address = discovery_info.address  # e.g. 'C8:47:8C:12:34:56'

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=address,
            data={"device_mac": address},
        )

    # ──────────────────────────────────────────────────────────────
    # YAML import fallback (not used, but keeps HA happy)
    # ──────────────────────────────────────────────────────────────
    async def async_step_import(self, import_config):
        """Support YAML→UI migration."""
        return await self.async_step_user(import_config)

    # ──────────────────────────────────────────────────────────────
    # Onboarding helper: listen for SOLEM devices during HA setup
    # ──────────────────────────────────────────────────────────────
    async def async_step_onboarding(self, user_input=None):
        """During onboarding, keep listening for BLE discoveries."""
        return await async_discovered_service_info(
            self.hass, self.async_step_bluetooth
        )
