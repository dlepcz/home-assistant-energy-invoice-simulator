from __future__ import annotations

from typing import Any

from homeassistant import config_entries

from .const import DEFAULT_NAME, DOMAIN


class PseRceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PSE RCE."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=DEFAULT_NAME,
            data={},
        )
