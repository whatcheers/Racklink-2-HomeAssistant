"""Config flow for RackLink integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DEFAULT_PORT, DEFAULT_USERNAME, DOMAIN, PROTOCOL_PORT
from .protocol import RackLinkProtocol

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RackLink."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        # Validate connection
        client = RackLinkProtocol(
            user_input[CONF_HOST], user_input.get(CONF_PORT, DEFAULT_PORT)
        )
        try:
            if not await client.connect():
                errors["base"] = "cannot_connect"
            elif not await client.login(
                user_input.get(CONF_USERNAME, DEFAULT_USERNAME),
                user_input[CONF_PASSWORD],
            ):
                errors["base"] = "invalid_auth"
            else:
                await client.disconnect()
        except Exception as err:
            _LOGGER.exception("Unexpected exception during config flow: %s", err)
            errors["base"] = "unknown"
        finally:
            await client.disconnect()

        if errors:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
            )

        return self.async_create_entry(
            title=f"RackLink {user_input[CONF_HOST]}",
            data=user_input,
        )
