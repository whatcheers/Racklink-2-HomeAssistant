"""Switch platform for RackLink power outlets."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up RackLink switch entities."""
    coordinator: RackLinkCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for first update to get outlet count
    await coordinator.async_config_entry_first_refresh()

    outlets = coordinator.data.get("outlets", {})
    entities = [
        RackLinkOutlet(coordinator, outlet_index, outlet_data)
        for outlet_index, outlet_data in outlets.items()
    ]

    async_add_entities(entities)


class RackLinkOutlet(CoordinatorEntity, SwitchEntity):
    """Representation of a RackLink power outlet."""

    def __init__(
        self,
        coordinator: RackLinkCoordinator,
        outlet_index: int,
        outlet_data: dict,
    ) -> None:
        """Initialize the outlet."""
        super().__init__(coordinator)
        self._outlet_index = outlet_index
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_outlet_{outlet_index}"
        self._attr_name = outlet_data.get("name", f"Outlet {outlet_index}")
        self._attr_is_on = outlet_data.get("state", False)

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
    def is_on(self) -> bool:
        """Return true if outlet is on."""
        outlet_data = self.coordinator.data.get("outlets", {}).get(self._outlet_index, {})
        return outlet_data.get("state", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the outlet on."""
        success = await self.coordinator.client.set_outlet_state(self._outlet_index, True)
        if success:
            # Update local state immediately
            if "outlets" not in self.coordinator.data:
                self.coordinator.data["outlets"] = {}
            if self._outlet_index not in self.coordinator.data["outlets"]:
                self.coordinator.data["outlets"][self._outlet_index] = {}
            self.coordinator.data["outlets"][self._outlet_index]["state"] = True
            self.async_write_ha_state()
            # Trigger a refresh to get updated state
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn on outlet %d", self._outlet_index)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the outlet off."""
        success = await self.coordinator.client.set_outlet_state(self._outlet_index, False)
        if success:
            # Update local state immediately
            if "outlets" not in self.coordinator.data:
                self.coordinator.data["outlets"] = {}
            if self._outlet_index not in self.coordinator.data["outlets"]:
                self.coordinator.data["outlets"][self._outlet_index] = {}
            self.coordinator.data["outlets"][self._outlet_index]["state"] = False
            self.async_write_ha_state()
            # Trigger a refresh to get updated state
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn off outlet %d", self._outlet_index)
