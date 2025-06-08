"""Switch platform for Solem."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SolemDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SolemDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SolemSprinklerSwitch(coordinator)])

class SolemSprinklerSwitch(SwitchEntity):
    """Representation of the Solem sprinkler as a switch."""

    def __init__(self, coordinator: SolemDataUpdateCoordinator) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{coordinator._mac}_sprinkler"
        self._attr_name = "Solem Sprinkler"

    @property
    def available(self):
        return self._coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        return self._coordinator.data.get("is_watering", False) if self._coordinator.data else False

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(self._coordinator._client.start_watering)
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._coordinator._client.stop_watering)
        await self._coordinator.async_request_refresh()

    async def async_update(self):
        await self._coordinator.async_request_refresh()
