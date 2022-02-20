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
    """Set up switch platform."""
    coordinator = hass.data[DOMAIN][config_entry.unique_id]
    entities: list[SwitchEntity] = []
    for vehicle_id in coordinator.vehicle_manager.vehicles.keys():
        vehicle: Vehicle = coordinator.vehicle_manager.vehicles[vehicle_id]
        entities.append(HyundaiKiaChargeSwitch(coordinator, vehicle))
        entities.append(HyundaiKiaDoorsLockSwitch(coordinator, vehicle))
    async_add_entities(entities)


class HyundaiKiaChargeSwitch(HyundaiKiaConnectEntity, SwitchEntity):
    """Hyundai / Kia Connect Charge on/off switch."""

    vehicle_manager: VehicleManager
    vehicle: Vehicle

    def __init__(
        self,
        coordinator: HyundaiKiaConnectDataUpdateCoordinator,
        vehicle: Vehicle,
    ) -> None:
        """Initialize the Charge toggle."""
        super().__init__(coordinator, vehicle)
        self.entity_description = SwitchEntityDescription(
            icon="mdi:power-plug",
            device_class=SwitchDeviceClass.SWITCH,
            key=f"{DOMAIN}_{vehicle.id}_charge",
            name=f"{vehicle.name} Charge Switch",
        )
        self.vehicle_manager = coordinator.vehicle_manager
        self._attr_unique_id = f"{DOMAIN}_{vehicle.id}_charge"

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


class HyundaiKiaDoorsLockSwitch(HyundaiKiaConnectEntity, SwitchEntity):
    """Hyundai / Kia Connect Door Lock."""

    vehicle_manager: VehicleManager
    vehicle: Vehicle

    def __init__(
        self,
        coordinator: HyundaiKiaConnectDataUpdateCoordinator,
        vehicle: Vehicle,
    ) -> None:
        """Initialize the Car Lock Toggle."""
        super().__init__(coordinator, vehicle)
        self.entity_description = SwitchEntityDescription(
            icon="mdi:car-door-lock",
            device_class=SwitchDeviceClass.SWITCH,
            key=f"{DOMAIN}_{vehicle.id}_door_lock",
            name=f"{vehicle.name} Door Lock",
        )
        self.vehicle_manager = coordinator.vehicle_manager
        self._attr_unique_id = f"{DOMAIN}_{vehicle.id}_door_lock"

    @property
    def is_on(self) -> bool:
        """Is vehicle locked."""
        return self.vehicle.is_locked

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Lock car."""
        self.vehicle_manager.api.lock_action(
            self.vehicle_manager.token, self.vehicle, "close"
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Unlock car."""
        self.vehicle_manager.api.lock_action(
            self.vehicle_manager.token, self.vehicle, "open"
        )
