"""DataUpdateCoordinator for RackLink."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
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
        _LOGGER.debug("Starting data update")
        try:
            # Ensure we're connected
            if not self.client._connected:
                _LOGGER.info("Not connected, establishing connection...")
                _LOGGER.debug("Connecting to %s:%d", self.client.host, self.client.port)
                if not await self.client.connect():
                    _LOGGER.error("Connection failed to %s:%d", self.client.host, self.client.port)
                    raise UpdateFailed("Failed to connect to RackLink device")
                _LOGGER.debug("TCP connection established, attempting login...")
                if not await self.client.login(self.username, self.password):
                    _LOGGER.error("Login failed for user: %s", self.username)
                    await self.client.disconnect()
                    raise UpdateFailed("Failed to login to RackLink device")
                _LOGGER.debug("Login successful")

            # Test connection with a real command (outlet count)
            # This serves as both connection test and initialization
            if self._outlet_count is None:
                _LOGGER.debug("Fetching outlet count...")
                count = await self.client.get_outlet_count()
                if count is None:
                    # If we can't get count, connection might be lost
                    _LOGGER.warning("Failed to get outlet count, connection may be lost")
                    _LOGGER.debug("Attempting reconnection...")
                    await self.client.disconnect()
                    if not await self.client.connect():
                        _LOGGER.error("Reconnection failed")
                        raise UpdateFailed("Failed to reconnect to RackLink device")
                    if not await self.client.login(self.username, self.password):
                        _LOGGER.error("Re-login failed")
                        await self.client.disconnect()
                        raise UpdateFailed("Failed to re-login to RackLink device")
                    # Try again
                    _LOGGER.debug("Retrying outlet count after reconnection...")
                    count = await self.client.get_outlet_count()
                    if count is None:
                        _LOGGER.warning("Using default outlet count of 8")
                        self._outlet_count = 8  # Default fallback
                    else:
                        # Safety: Cap at 8 (RLNK-SW715R has 8 outlets)
                        if count > 16:
                            _LOGGER.warning("Outlet count %d seems invalid, defaulting to 8", count)
                            count = 8
                        _LOGGER.debug("Outlet count retrieved: %d", count)
                        self._outlet_count = count
                else:
                    # Safety: Cap at 8 (RLNK-SW715R has 8 outlets)
                    if count > 16:
                        _LOGGER.warning("Outlet count %d seems invalid, defaulting to 8", count)
                        count = 8
                    _LOGGER.debug("Outlet count: %d", count)
                    self._outlet_count = count

            # Just fetch outlet names for now - keep it simple
            # Safety: Cap outlet count at 8 (RLNK-SW715R has 8 outlets)
            outlet_count = min(self._outlet_count or 8, 8)
            _LOGGER.debug("Fetching outlet names for %d outlets (capped at 16)", outlet_count)
            outlets: dict[int, dict] = {}
            for i in range(1, outlet_count + 1):
                try:
                    # Check connection before each request
                    if not self.client._connected:
                        _LOGGER.warning("Connection lost, reconnecting before fetching outlet %d name...", i)
                        await self.client.disconnect()
                        if not await self.client.connect():
                            _LOGGER.error("Failed to reconnect")
                            break
                        if not await self.client.login(self.username, self.password):
                            _LOGGER.error("Failed to re-login")
                            await self.client.disconnect()
                            break
                    
                    _LOGGER.debug("Fetching outlet %d name...", i)
                    name = await self.client.get_outlet_name(i)
                    _LOGGER.debug("Outlet %d name: %s", i, name)
                    outlets[i] = {
                        "name": name or f"Outlet {i}",
                    }
                except ConnectionError:
                    _LOGGER.warning("Connection lost while fetching outlet %d name, will retry next update", i)
                    outlets[i] = {
                        "name": f"Outlet {i}",
                    }
                    # Mark as disconnected so we reconnect next time
                    self.client._connected = False
                except Exception as outlet_err:
                    _LOGGER.warning("Error fetching outlet %d name: %s", i, outlet_err, exc_info=True)
                    # Continue with other outlets
                    outlets[i] = {
                        "name": f"Outlet {i}",
                    }

            _LOGGER.debug("Data update complete: %d outlets", len(outlets))
            return {
                "outlets": outlets,
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
