"""sd"""

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import BaseEntity
from .const import DOMAIN, INVOICE_INPUT_NUMBERS
from .invoice_coordinator import InvoiceCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PSE RCE sensors from a config entry."""
    # rce_pse_coordinator: PseRceDataUpdateCoordinator = hass.data[DOMAIN][
    #    entry.entry_id
    # ]["rce_pse"]
    invoice_coordinator: InvoiceCoordinator = hass.data[DOMAIN][entry.entry_id][
        "invoice"
    ]

    entities = []
    for tid, cfg in INVOICE_INPUT_NUMBERS.items():
        name = str(cfg.get("name", tid))
        min_value = cfg.get("min", 0)
        max_value = cfg.get("max", 1000000)
        step = cfg.get("step", 1)
        unit = cfg.get("unit_of_measurement", None)

        entityDescription = NumberEntityDescription(
            key=tid,
            name=name,
            native_min_value=min_value,
            native_max_value=max_value,
            native_step=step,
            native_unit_of_measurement=unit,
        )
        entities.append(
            InvoiceInputNumber(
                invoice_coordinator,
                entityDescription,
            )
        )

    async_add_entities(entities)


class InvoiceInputNumber(BaseEntity, NumberEntity):
    """Base sensor for invoice."""

    def __init__(
        self,
        coordinator: InvoiceCoordinator,
        description: NumberEntityDescription,
    ) -> None:
        """Inicjalizuje encję sensora Invoice."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.coordinator.name}_{description.key}"
