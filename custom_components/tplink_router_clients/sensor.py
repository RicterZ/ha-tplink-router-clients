from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CARD_MODE,
    CONF_COLUMNS,
    DEFAULT_CARD_MODE,
    DEFAULT_COLUMNS,
    DOMAIN,
)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([OnlineClientsSensor(hass.data[DOMAIN][entry.entry_id], entry)])


class OnlineClientsSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Online clients"
    _attr_icon = "mdi:lan-connect"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_online_clients"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="TP-Link Router Clients",
            manufacturer="TP-Link",
        )

    @property
    def native_value(self):
        return len(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        return {
            "clients": self.coordinator.data,
            CONF_CARD_MODE: self.entry.options.get(CONF_CARD_MODE, DEFAULT_CARD_MODE),
            CONF_COLUMNS: self.entry.options.get(CONF_COLUMNS, DEFAULT_COLUMNS),
        }

