from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .invoice_coordinator import InvoiceCoordinator
from .pse_rce_coordinator import PseRceDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the PSE RCE integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PSE RCE from a config entry."""
    pse_rce_coordinator = PseRceDataUpdateCoordinator(hass, entry)
    invoice_coordinator = InvoiceCoordinator(hass, entry)

    await pse_rce_coordinator.async_config_entry_first_refresh()
    await invoice_coordinator.async_config_entry_first_refresh()
    await pse_rce_coordinator.async_start_listeners()
    await invoice_coordinator.async_start_listeners()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "pse_rce": pse_rce_coordinator,
        "invoice": invoice_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Ud a config entry."""
    coordinator: PseRceDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["1"]
    await coordinator.async_stop_listeners()

    coordinator1: PseRceDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["2"]
    await coordinator1.async_stop_listeners()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)

    return unload_ok


class InvoiceBaseEntity(CoordinatorEntity[InvoiceCoordinator]):
    """Main class for Evopell entities."""

    def __init__(self, coordinator: InvoiceCoordinator) -> None:
        """Inicjalizacja encji powiązanej z koordynatorem."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo | None:
        """Device info."""
        return self.coordinator.device_info


class BaseEntity(CoordinatorEntity[PseRceDataUpdateCoordinator]):
    """Main class for Evopell entities."""

    def __init__(self, coordinator: PseRceDataUpdateCoordinator) -> None:
        """Inicjalizacja encji powiązanej z koordynatorem."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo | None:
        """Device info."""
        return self.coordinator.device_info
