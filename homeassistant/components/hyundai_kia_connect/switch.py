"""Switches for Hyundai / Kia Connect integration."""
from __future__ import annotations

import logging
from typing import Any

from hyundai_kia_connect_api import Vehicle, VehicleManager

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HyundaiKiaConnectDataUpdateCoordinator
from .entity import HyundaiKiaConnectEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary_sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.unique_id]
    for vehicle_id in coordinator.vehicle_manager.vehicles.keys():
        vehicle: Vehicle = coordinator.vehicle_manager.vehicles[vehicle_id]
        async_add_entities([HyundaiKiaChargeSwitch(coordinator, vehicle)])


class HyundaiKiaChargeSwitch(HyundaiKiaConnectEntity, SwitchEntity):
    """Hyundai / Kia Connect Charge on/off switch."""

    vehicle_manager: VehicleManager
    vehicle: Vehicle

    def __init__(
        self,
        coordinator: HyundaiKiaConnectDataUpdateCoordinator,
        vehicle: Vehicle,
    ) -> None:
        """Initialize the Climate Control."""
        super().__init__(coordinator, vehicle)
        self.entity_description = SwitchEntityDescription(
            icon="mdi:power-plug",
            device_class=SwitchDeviceClass.SWITCH,
            key=f"{DOMAIN}_{vehicle.id}_charge",
            name=f"{vehicle.name} Charge Switch",
        )
        self.vehicle_manager = coordinator.vehicle_manager
        self._attr_unique_id = f"{DOMAIN}_{vehicle.id}_charge"
        self._attr_name = f"{vehicle.name} Charge Switch"

    @property
    def is_on(self) -> bool:
        """Is the vehicle currently supposed to be charging?."""
        return self.vehicle.ev_battery_is_charging

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on charging."""
        await self.hass.async_add_executor_job(
            self.vehicle_manager.api.start_charge(
                self.vehicle_manager.token, self.vehicle
            )
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off charging."""
        await self.hass.async_add_executor_job(
            self.vehicle_manager.api.stop_charge(
                self.vehicle_manager.token, self.vehicle
            )
        )
