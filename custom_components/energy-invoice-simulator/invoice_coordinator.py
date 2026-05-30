from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed, UpdateFailed
from homeassistant.util import dt as dt_util


class InvoiceCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinator to fetch and normalize PSE RCE data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logging.getLogger(__name__),
            name="Invoice Coordinator",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the source."""
        try:
            # Replace this with your actual logic to fetch data
            # result = await self.session.fetch_energy_data()
            # return result

            # Placeholder for demonstration:
            data = {"cost": 10.5, "usage": 100}
            return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
            
    async def async_start_listeners(self) -> None:
        """Start time-based listeners."""