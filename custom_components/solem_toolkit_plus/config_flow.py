"""Config flow for the Solem Toolkit Plus integration (BLE discovery + manual entry)."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import callback
from homeassistant.components.bluetooth import BluetoothServiceInfo

from .const import DOMAIN, COMPANY_ID_SOLEM, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)


class SolemConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solem Toolkit Plus."""

    VERSION = 1

    # ────────────────────────────────────────── Manual setup
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Let the user enter the MAC address manually."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    # ────────────────────────────────────────── Automatic BLE discovery
    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfo):
        """Triggered automatically by HA when a matching BLE advertisement is received."""
        _LOGGER.debug("Received Bluetooth advertisement: %s", discovery_info)

        # Extra safety: ignore packets that do not carry Solem's company ID.
        if COMPANY_ID_SOLEM not in discovery_info.manufacturer_data:
            return self.async_abort(reason="not_solem")

        address = discovery_info.address  # e.g. "C8:47:8C:12:34:56"

        # Abort if this device is already configured.
        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"Solem {address[-5:]}",
            data={CONF_ADDRESS: address, CONF_NAME: DEFAULT_NAME},
        )

    # ────────────────────────────────────────── Options flow (placeholder)
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler (not implemented yet)."""
        return SolemOptionsFlowHandler(config_entry)


class SolemOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for an existing entry (currently empty)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_create_entry(title="", data={})
