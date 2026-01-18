"""DataUpdateCoordinator for RackLink."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CMD_PING, CMD_SENSORS_START, DOMAIN, SUB_GET
from .protocol import RackLinkProtocol

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class RackLinkCoordinator(DataUpdateCoordinator):
    """Class to manage fetching RackLink data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.client = RackLinkProtocol(
            entry.data["host"],
            entry.data.get("port", 60000),
        )
        self.username = entry.data.get("username", "user")
        self.password = entry.data["password"]
        self._outlet_count: int | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from RackLink."""
        try:
            # Ensure we're connected
            if not self.client._connected:
                _LOGGER.info("Not connected, establishing connection...")
                if not await self.client.connect():
                    raise UpdateFailed("Failed to connect to RackLink device")
                if not await self.client.login(self.username, self.password):
                    await self.client.disconnect()
                    raise UpdateFailed("Failed to login to RackLink device")

            # Try to ping to keep connection alive (optional - some devices don't respond to client pings)
            # If ping fails, we'll test with a real command instead
            try:
                ping_result = await self.client.ping()
                if not ping_result:
                    _LOGGER.debug("Ping failed (device may not support client-initiated pings, will test with command)")
                    # Don't fail here - test connection with actual command instead
            except Exception as ping_err:
                _LOGGER.debug("Ping error: %s (non-fatal, will test with command)", ping_err)

            # Get outlet count if we don't have it
            if self._outlet_count is None:
                self._outlet_count = await self.client.get_outlet_count()
                if self._outlet_count is None:
                    self._outlet_count = 8  # Default fallback

            # Fetch outlet states
            outlets: dict[int, dict] = {}
            for i in range(1, (self._outlet_count or 8) + 1):
                state = await self.client.get_outlet_state(i)
                name = await self.client.get_outlet_name(i)
                outlets[i] = {
                    "state": state,
                    "name": name or f"Outlet {i}",
                }

            # Fetch sensor data (temperature, voltage, current, etc.)
            sensors: dict[str, float | None] = {}
            # Sensor commands are 0x50-0x61 per protocol manual
            # For now, fetch basic sensors
            # TODO: Implement full sensor reading based on protocol manual

            return {
                "outlets": outlets,
                "sensors": sensors,
                "connected": True,
            }
        except UpdateFailed:
            # Re-raise UpdateFailed as-is
            raise
        except Exception as err:
            _LOGGER.error("Error communicating with RackLink: %s", err, exc_info=True)
            # Mark as disconnected on any error
            if self.client._connected:
                try:
                    await self.client.disconnect()
                except:
                    pass
            raise UpdateFailed(f"Error communicating with RackLink: {err}") from err
