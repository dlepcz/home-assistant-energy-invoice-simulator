"""Config flow for Invoice simulator integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .const import CONF_EXPORT_SENSOR, CONF_IMPORT_SENSOR, DOMAIN


def _is_valid_energy_sensor(hass: HomeAssistant, entity_id: str) -> bool:
    """Validate that entity is an energy sensor."""
    state = hass.states.get(entity_id)
    if state is None:
        return False

    device_class = state.attributes.get("device_class")
    unit = state.attributes.get("unit_of_measurement")
    state_class = state.attributes.get("state_class")

    return (
        device_class == "energy"
        and unit in {"Wh", "kWh", "MWh"}
        and state_class in {"total", "total_increasing", None}
    )


class InvoiceSimulatorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Invoice simulator."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            import_sensor = user_input[CONF_IMPORT_SENSOR]
            export_sensor = user_input[CONF_EXPORT_SENSOR]

            if not _is_valid_energy_sensor(self.hass, import_sensor):
                errors["base"] = "invalid_import_sensor"

            elif not _is_valid_energy_sensor(self.hass, export_sensor):
                errors["base"] = "invalid_export_sensor"

            else:
                await self.async_set_unique_id(f"{import_sensor}-{export_sensor}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "Invoice simulator"),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="Invoice simulator"): str,
                    vol.Required(CONF_IMPORT_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                        )
                    ),
                    vol.Required(CONF_EXPORT_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                        )
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return options flow."""
        return InvoiceSimulatorOptionsFlow()


class InvoiceSimulatorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            import_sensor = user_input[CONF_IMPORT_SENSOR]
            export_sensor = user_input[CONF_EXPORT_SENSOR]

            if not _is_valid_energy_sensor(self.hass, import_sensor):
                errors["base"] = "invalid_import_sensor"

            elif not _is_valid_energy_sensor(self.hass, export_sensor):
                errors["base"] = "invalid_export_sensor"

            else:
                return self.async_create_entry(title="", data=user_input)

        current_import_sensor = self.config_entry.options.get(
            CONF_IMPORT_SENSOR,
            self.config_entry.data.get(CONF_IMPORT_SENSOR, ""),
        )

        current_export_sensor = self.config_entry.options.get(
            CONF_EXPORT_SENSOR,
            self.config_entry.data.get(CONF_EXPORT_SENSOR, ""),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IMPORT_SENSOR,
                        default=current_import_sensor,
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Required(
                        CONF_EXPORT_SENSOR,
                        default=current_export_sensor,
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                }
            ),
            errors=errors,
        )
