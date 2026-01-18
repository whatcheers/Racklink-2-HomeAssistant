"""Sensor platform for RackLink monitoring."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import RackLinkCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RackLink sensor entities."""
    coordinator: RackLinkCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for first update
    await coordinator.async_config_entry_first_refresh()

    # Create sensor entities
    # TODO: Add more sensors based on protocol manual (0x50-0x61)
    entities: list[SensorEntity] = [
        RackLinkConnectionSensor(coordinator),
    ]

    async_add_entities(entities)


class RackLinkConnectionSensor(CoordinatorEntity, SensorEntity):
    """Representation of RackLink connection status."""

    _attr_name = "Connection Status"
    _attr_native_value = "Connected"
    _attr_icon = "mdi:network"

    def __init__(self, coordinator: RackLinkCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_connection"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=f"RackLink {self.coordinator.client.host}",
            manufacturer=MANUFACTURER,
            model="RackLink",
        )

    @property
    def native_value(self) -> str:
        """Return the connection status."""
        if self.coordinator.data.get("connected", False):
            return "Connected"
        return "Disconnected"
