"""Config flow for the Lux Trash integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_LOCATION,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_URL,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LOCATION): str,
        vol.Required(
            CONF_URL,
            default="https://www.valorlux.lu/manager/mod/valorlux/valorlux/all?v=110&lang=fr",
        ): str,
        vol.Required(CONF_TIMEOUT, default=10): int,
        vol.Required(CONF_SCAN_INTERVAL, default=30, msg="Refresh interval"): int,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    session = async_get_clientsession(hass)
    async with asyncio.timeout(data[CONF_TIMEOUT]):
        resp = await session.get(data[CONF_URL])
        body = await resp.text()

        if resp.ok:
            _LOGGER.info("Lux Trash valorlux URL confirmed working")
            _LOGGER.debug(body)
        else:
            _LOGGER.error("Lux Trash valorlux URL not working")
            raise CannotConnect

    return {"title": "Lux Trash"}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lux Trash."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
