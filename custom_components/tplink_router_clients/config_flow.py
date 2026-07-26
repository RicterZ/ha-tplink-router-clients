import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector

from .api import RouterClient, RouterError
from .const import (
    CONF_CARD_MODE,
    CONF_COLUMNS,
    CONF_SCAN_INTERVAL,
    DEFAULT_CARD_MODE,
    DEFAULT_COLUMNS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

CARD_MODES = [
    {"value": "table", "label": "Table"},
    {"value": "compact", "label": "Compact"},
]
COLUMNS = [
    {"value": "name", "label": "Device"},
    {"value": "mac", "label": "MAC"},
    {"value": "ip", "label": "IP"},
    {"value": "up", "label": "Up"},
    {"value": "down", "label": "Down"},
]


def options_schema(options):
    return vol.Schema({
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ): selector.NumberSelector(selector.NumberSelectorConfig(
            min=2, max=300, step=1, unit_of_measurement="seconds"
        )),
        vol.Required(
            CONF_CARD_MODE,
            default=options.get(CONF_CARD_MODE, DEFAULT_CARD_MODE),
        ): selector.SelectSelector(selector.SelectSelectorConfig(options=CARD_MODES)),
        vol.Required(
            CONF_COLUMNS,
            default=options.get(CONF_COLUMNS, DEFAULT_COLUMNS),
        ): selector.SelectSelector(selector.SelectSelectorConfig(
            options=COLUMNS, multiple=True
        )),
    })


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            host = user_input[CONF_HOST].strip()
            client = RouterClient(
                host, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            try:
                await self.hass.async_add_executor_job(client.online_clients)
            except RouterError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(host.lower())
                self._abort_if_unique_id_configured()
                data = {
                    CONF_HOST: host,
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }
                options = {key: user_input[key] for key in (
                    CONF_SCAN_INTERVAL, CONF_CARD_MODE, CONF_COLUMNS
                )}
                return self.async_create_entry(
                    title=host, data=data, options=options
                )

        defaults = user_input or {}
        schema = vol.Schema({
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): str,
            vol.Required(CONF_USERNAME, default=defaults.get(CONF_USERNAME, "admin")): str,
            vol.Required(CONF_PASSWORD): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
        }).extend(options_schema(defaults).schema)
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlow()


class OptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init", data_schema=options_schema(self.config_entry.options)
        )
