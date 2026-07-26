from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import RouterCoordinator

PLATFORMS = [Platform.SENSOR]
CARD_URL = "/tplink_router_clients/tplink-router-clients-card.js"


async def async_setup_entry(hass, entry):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                CARD_URL,
                str(Path(__file__).parent / "www" / "tplink-router-clients-card.js"),
                True,
            )
        ])

    coordinator = RouterCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    return False


async def async_reload_entry(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

