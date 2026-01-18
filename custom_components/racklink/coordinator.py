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
                        _LOGGER.debug("Outlet count retrieved: %d", count)
                        self._outlet_count = count
                else:
                    _LOGGER.debug("Outlet count: %d", count)
                    self._outlet_count = count

            # Fetch outlet states
            _LOGGER.debug("Fetching outlet states for %d outlets", self._outlet_count or 8)
            outlets: dict[int, dict] = {}
            outlet_count = self._outlet_count or 8
            for i in range(1, outlet_count + 1):
                try:
                    _LOGGER.debug("Fetching outlet %d state...", i)
                    state = await self.client.get_outlet_state(i)
                    _LOGGER.debug("Outlet %d state: %s", i, "ON" if state else "OFF" if state is not None else "UNKNOWN")
                    name = await self.client.get_outlet_name(i)
                    _LOGGER.debug("Outlet %d name: %s", i, name)
                    outlets[i] = {
                        "state": state,
                        "name": name or f"Outlet {i}",
                    }
                except Exception as outlet_err:
                    _LOGGER.warning("Error fetching outlet %d: %s", i, outlet_err, exc_info=True)
                    # Continue with other outlets
                    outlets[i] = {
                        "state": None,
                        "name": f"Outlet {i}",
                    }

            # Fetch sensor data (temperature, voltage, current, power, etc.)
            _LOGGER.debug("Fetching sensor data...")
            sensors: dict[str, float | None] = {}
            try:
                # Temperature (0x50)
                _LOGGER.debug("Reading temperature (0x50)...")
                temp = await self.client.get_temperature()
                if temp is not None:
                    _LOGGER.debug("Temperature: %.1f°F", temp)
                    sensors["temperature"] = temp
                else:
                    _LOGGER.debug("Temperature: No data")
                
                # Voltage RMS (0x51)
                _LOGGER.debug("Reading voltage (0x51)...")
                voltage = await self.client.get_voltage()
                if voltage is not None:
                    _LOGGER.debug("Voltage: %.1fV", voltage)
                    sensors["voltage"] = voltage
                else:
                    _LOGGER.debug("Voltage: No data")
                
                # Current RMS (0x52)
                _LOGGER.debug("Reading current (0x52)...")
                current = await self.client.get_current()
                if current is not None:
                    _LOGGER.debug("Current: %.2fA", current)
                    sensors["current"] = current
                else:
                    _LOGGER.debug("Current: No data")
                
                # Power/Wattage (0x53)
                _LOGGER.debug("Reading power (0x53)...")
                power = await self.client.get_power()
                if power is not None:
                    _LOGGER.debug("Power: %.1fW", power)
                    sensors["power"] = power
                else:
                    _LOGGER.debug("Power: No data")
                
                # Power Factor (0x54)
                _LOGGER.debug("Reading power factor (0x54)...")
                power_factor = await self.client.get_power_factor()
                if power_factor is not None:
                    _LOGGER.debug("Power Factor: %.3f", power_factor)
                    sensors["power_factor"] = power_factor
                else:
                    _LOGGER.debug("Power Factor: No data")
                
                # Thermal Load (0x55)
                _LOGGER.debug("Reading thermal load (0x55)...")
                thermal_load = await self.client.get_thermal_load()
                if thermal_load is not None:
                    _LOGGER.debug("Thermal Load: %.1f", thermal_load)
                    sensors["thermal_load"] = thermal_load
                else:
                    _LOGGER.debug("Thermal Load: No data")
                
                # Occupancy (0x56)
                _LOGGER.debug("Reading occupancy (0x56)...")
                occupancy = await self.client.get_occupancy()
                if occupancy is not None:
                    _LOGGER.debug("Occupancy: %.0f", occupancy)
                    sensors["occupancy"] = occupancy
                else:
                    _LOGGER.debug("Occupancy: No data")
                    
                _LOGGER.debug("Sensor data fetch complete. Got %d sensors", len(sensors))
            except Exception as sensor_err:
                _LOGGER.warning("Error fetching sensors: %s", sensor_err, exc_info=True)

            _LOGGER.debug("Data update complete: %d outlets, %d sensors", 
                         len(outlets), len(sensors))
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
