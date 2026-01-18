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
    entities: list[SensorEntity] = [
        RackLinkConnectionSensor(coordinator),
        RackLinkTemperatureSensor(coordinator),
        RackLinkVoltageSensor(coordinator),
        RackLinkCurrentSensor(coordinator),
        RackLinkPowerSensor(coordinator),
        RackLinkPowerFactorSensor(coordinator),
        RackLinkThermalLoadSensor(coordinator),
        RackLinkOccupancySensor(coordinator),
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


class RackLinkTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Representation of RackLink temperature sensor."""

    _attr_name = "Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: RackLinkCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_temperature"

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
    def native_value(self) -> float | None:
        """Return the temperature."""
        return self.coordinator.data.get("sensors", {}).get("temperature")


class RackLinkVoltageSensor(CoordinatorEntity, SensorEntity):
    """Representation of RackLink voltage sensor."""

    _attr_name = "Voltage"
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:lightning-bolt"

    def __init__(self, coordinator: RackLinkCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_voltage"

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
    def native_value(self) -> float | None:
        """Return the voltage."""
        return self.coordinator.data.get("sensors", {}).get("voltage")


class RackLinkCurrentSensor(CoordinatorEntity, SensorEntity):
    """Representation of RackLink current sensor."""

    _attr_name = "Current"
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:current-ac"

    def __init__(self, coordinator: RackLinkCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_current"

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
    def native_value(self) -> float | None:
        """Return the current."""
        return self.coordinator.data.get("sensors", {}).get("current")


class RackLinkPowerSensor(CoordinatorEntity, SensorEntity):
    """Representation of RackLink power sensor."""

    _attr_name = "Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:flash"

    def __init__(self, coordinator: RackLinkCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_power"

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
    def native_value(self) -> float | None:
        """Return the power."""
        return self.coordinator.data.get("sensors", {}).get("power")


class RackLinkPowerFactorSensor(CoordinatorEntity, SensorEntity):
    """Representation of RackLink power factor sensor."""

    _attr_name = "Power Factor"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:sine-wave"

    def __init__(self, coordinator: RackLinkCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_power_factor"

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
    def native_value(self) -> float | None:
        """Return the power factor."""
        return self.coordinator.data.get("sensors", {}).get("power_factor")


class RackLinkThermalLoadSensor(CoordinatorEntity, SensorEntity):
    """Representation of RackLink thermal load sensor."""

    _attr_name = "Thermal Load"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:heat-wave"

    def __init__(self, coordinator: RackLinkCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_thermal_load"

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
    def native_value(self) -> float | None:
        """Return the thermal load."""
        return self.coordinator.data.get("sensors", {}).get("thermal_load")


class RackLinkOccupancySensor(CoordinatorEntity, SensorEntity):
    """Representation of RackLink occupancy sensor."""

    _attr_name = "Occupancy"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:motion-sensor"

    def __init__(self, coordinator: RackLinkCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_occupancy"

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
    def native_value(self) -> float | None:
        """Return the occupancy."""
        return self.coordinator.data.get("sensors", {}).get("occupancy")
