"""Sensor platform for Solem."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SolemDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SolemDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SolemBatterySensor(coordinator)])

class SolemBatterySensor(SensorEntity):
    """Battery level of the Solem device."""

    _attr_device_class = "battery"
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator: SolemDataUpdateCoordinator):
        self._coordinator = coordinator
        self._attr_unique_id = f"{coordinator._mac}_battery"
        self._attr_name = "Solem Battery"

    @property
    def available(self):
        return self._coordinator.last_update_success

    @property
    def native_value(self):
        return self._coordinator.data.get("battery", None) if self._coordinator.data else None

    async def async_update(self):
        await self._coordinator.async_request_refresh()
