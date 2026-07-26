import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RouterClient, RouterError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

LOGGER = logging.getLogger(__name__)


class RouterCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.client = RouterClient(
            entry.data["host"], entry.data["username"], entry.data["password"]
        )
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self.client.online_clients)
        except RouterError as error:
            raise UpdateFailed(str(error)) from error
