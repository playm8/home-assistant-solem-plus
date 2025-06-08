import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

try:
    # Re‑use the SolemClient already present in the repo
    from .solem import SolemClient
except ImportError:  # pragma: no cover
    SolemClient = None  # type: ignore

class SolemDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to poll Solem device status."""

    def __init__(self, hass: HomeAssistant, mac: str) -> None:
        self._mac = mac
        self._client = SolemClient(mac) if SolemClient else None

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{mac}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from Solem."""
        if self._client is None:
            raise UpdateFailed("SolemClient unavailable")

        try:
            return await self.hass.async_add_executor_job(self._client.get_status)
        except Exception as err:  # pragma: no cover
            raise UpdateFailed(err) from err
