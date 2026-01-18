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
        try:
            # Ensure we're connected
            if not self.client._connected:
                _LOGGER.info("Not connected, establishing connection...")
                if not await self.client.connect():
                    raise UpdateFailed("Failed to connect to RackLink device")
                if not await self.client.login(self.username, self.password):
                    await self.client.disconnect()
                    raise UpdateFailed("Failed to login to RackLink device")

            # Test connection with a real command (outlet count)
            # This serves as both connection test and initialization
            if self._outlet_count is None:
                count = await self.client.get_outlet_count()
                if count is None:
                    # If we can't get count, connection might be lost
                    _LOGGER.warning("Failed to get outlet count, connection may be lost")
                    # Try to reconnect
                    await self.client.disconnect()
                    if not await self.client.connect():
                        raise UpdateFailed("Failed to reconnect to RackLink device")
                    if not await self.client.login(self.username, self.password):
                        await self.client.disconnect()
                        raise UpdateFailed("Failed to re-login to RackLink device")
                    # Try again
                    count = await self.client.get_outlet_count()
                    if count is None:
                        _LOGGER.warning("Using default outlet count of 8")
                        self._outlet_count = 8  # Default fallback
                    else:
                        self._outlet_count = count
                else:
                    self._outlet_count = count

            # Fetch outlet states
            outlets: dict[int, dict] = {}
            outlet_count = self._outlet_count or 8
            for i in range(1, outlet_count + 1):
                try:
                    state = await self.client.get_outlet_state(i)
                    name = await self.client.get_outlet_name(i)
                    outlets[i] = {
                        "state": state,
                        "name": name or f"Outlet {i}",
                    }
                except Exception as outlet_err:
                    _LOGGER.warning("Error fetching outlet %d: %s", i, outlet_err)
                    # Continue with other outlets
                    outlets[i] = {
                        "state": None,
                        "name": f"Outlet {i}",
                    }

            # Fetch sensor data (temperature, voltage, current, power, etc.)
            sensors: dict[str, float | None] = {}
            try:
                # Temperature (0x50)
                temp = await self.client.get_temperature()
                if temp is not None:
                    sensors["temperature"] = temp
                
                # Voltage RMS (0x51)
                voltage = await self.client.get_voltage()
                if voltage is not None:
                    sensors["voltage"] = voltage
                
                # Current RMS (0x52)
                current = await self.client.get_current()
                if current is not None:
                    sensors["current"] = current
                
                # Power/Wattage (0x53)
                power = await self.client.get_power()
                if power is not None:
                    sensors["power"] = power
                
                # Power Factor (0x54)
                power_factor = await self.client.get_power_factor()
                if power_factor is not None:
                    sensors["power_factor"] = power_factor
                
                # Thermal Load (0x55)
                thermal_load = await self.client.get_thermal_load()
                if thermal_load is not None:
                    sensors["thermal_load"] = thermal_load
                
                # Occupancy (0x56)
                occupancy = await self.client.get_occupancy()
                if occupancy is not None:
                    sensors["occupancy"] = occupancy
                    
            except Exception as sensor_err:
                _LOGGER.warning("Error fetching sensors: %s", sensor_err)

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
