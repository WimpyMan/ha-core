"""The Lux Trash integration."""

from __future__ import annotations

from homeassistant.components.lux_trash.const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_LOCATION,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_URL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Lux Trash from a config entry."""

    conf = config[DOMAIN]
    url = conf.get(CONF_URL)
    location = conf.get(CONF_LOCATION)
    update_interval = conf[CONF_SCAN_INTERVAL]
    timeout = conf.get[CONF_TIMEOUT]

    session = async_get_clientsession(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _update_valorlux(hass, session, url, auth_token):
    """Update FreeDNS."""
    params = None

    if url is None:
        url = UPDATE_URL

    if auth_token is not None:
        params = {}
        params[auth_token] = ""

    try:
        async with asyncio.timeout(TIMEOUT):
            resp = await session.get(url, params=params)
            body = await resp.text()

            if "has not changed" in body:
                # IP has not changed.
                _LOGGER.debug("FreeDNS update skipped: IP has not changed")
                return True

            if "ERROR" not in body:
                _LOGGER.debug("Updating FreeDNS was successful: %s", body)
                return True

            if "Invalid update URL" in body:
                _LOGGER.error("FreeDNS update token is invalid")
            else:
                _LOGGER.warning("Updating FreeDNS failed: %s", body)

    except aiohttp.ClientError:
        _LOGGER.warning("Can't connect to FreeDNS API")

    except TimeoutError:
        _LOGGER.warning("Timeout from FreeDNS API at %s", url)
