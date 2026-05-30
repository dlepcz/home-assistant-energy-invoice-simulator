from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BaseEntity
from .const import (
    CURRENCY_PLN,
    DOMAIN,
    SENSOR_KEY_AVERAGE_PRICE_TODAY,
    SENSOR_KEY_CURRENT_PRICE,
    SENSOR_KEY_MAX_PRICE_TODAY,
    SENSOR_KEY_MIN_PRICE_TODAY,
    SENSOR_KEY_NEXT_PRICE,
)
from .pse_rce_coordinator import PseRceDataUpdateCoordinator, QuarterPrice


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PSE RCE sensors from a config entry."""
    rce_pse_coordinator: PseRceDataUpdateCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]["pse_rce"]
    # coordinator1: PseRceDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["2"]

    entities: list[SensorEntity] = [
        PseRceCurrentPriceSensor(rce_pse_coordinator, entry),
        PseRceNextPriceSensor(rce_pse_coordinator, entry),
        PseRceMinPriceTodaySensor(rce_pse_coordinator, entry),
        PseRceMaxPriceTodaySensor(rce_pse_coordinator, entry),
        PseRceAveragePriceTodaySensor(rce_pse_coordinator, entry),
    ]

    entities.extend(
        PseRceQuarterPriceSensor(rce_pse_coordinator, entry, index)
        for index in range(96)
    )

    async_add_entities(entities)


class PseRceBaseSensor(
    BaseEntity, CoordinatorEntity[PseRceDataUpdateCoordinator], SensorEntity
):
    """Base sensor for PSE RCE."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = f"{CURRENCY_PLN}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash"

    def __init__(
        self,
        coordinator: PseRceDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        name: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_key = sensor_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        # self._attr_device_info = DeviceInfo(
        #    identifiers={(DOMAIN, entry.entry_id)},
        #    name="PSE RCE",
        #    manufacturer="PSE",
        #    model="RCE PLN API",
        # )


class PseRceCurrentPriceSensor(PseRceBaseSensor):
    """Current quarter price sensor."""

    def __init__(
        self,
        coordinator: PseRceDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            coordinator, entry, SENSOR_KEY_CURRENT_PRICE, "PSE current price"
        )

    @property
    def native_value(self) -> float | None:
        """Return current price in PLN/kWh."""
        item = self.coordinator.data.current_item
        return item.price_pln_per_kwh if item else None


class PseRceNextPriceSensor(PseRceBaseSensor):
    """Next quarter price sensor."""

    def __init__(
        self,
        coordinator: PseRceDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry, SENSOR_KEY_NEXT_PRICE, "PSE next price")

    @property
    def native_value(self) -> float | None:
        """Return next price in PLN/kWh."""
        item = self.coordinator.data.next_item
        return item.price_pln_per_kwh if item else None


class PseRceMinPriceTodaySensor(PseRceBaseSensor):
    """Minimum price today sensor."""

    def __init__(
        self,
        coordinator: PseRceDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            coordinator, entry, SENSOR_KEY_MIN_PRICE_TODAY, "Min price today"
        )

    @property
    def native_value(self) -> float | None:
        """Return minimum price today in PLN/kWh."""
        return self.coordinator.data.min_price_today


class PseRceMaxPriceTodaySensor(PseRceBaseSensor):
    """Maximum price today sensor."""

    def __init__(
        self,
        coordinator: PseRceDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            coordinator, entry, SENSOR_KEY_MAX_PRICE_TODAY, "Max price today"
        )

    @property
    def native_value(self) -> float | None:
        """Return maximum price today in PLN/kWh."""
        return self.coordinator.data.max_price_today


class PseRceAveragePriceTodaySensor(PseRceBaseSensor):
    """Average price today sensor."""

    def __init__(
        self,
        coordinator: PseRceDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            coordinator,
            entry,
            SENSOR_KEY_AVERAGE_PRICE_TODAY,
            "Average price today",
        )

    @property
    def native_value(self) -> float | None:
        """Return average price today in PLN/kWh."""
        return self.coordinator.data.average_price_today


class PseRceQuarterPriceSensor(PseRceBaseSensor):
    """Single quarter-of-day price sensor."""

    _attr_entity_registry_enabled_default = False
    _attr_icon = "mdi:chart-line"

    def __init__(
        self,
        coordinator: PseRceDataUpdateCoordinator,
        entry: ConfigEntry,
        quarter_index: int,
    ) -> None:
        """Initialize quarter sensor."""
        self._quarter_index = quarter_index

        start_hour = quarter_index // 4
        start_minute = (quarter_index % 4) * 15
        label = f"{start_hour:02d}:{start_minute:02d}"

        super().__init__(
            coordinator,
            entry,
            f"quarter_price_{quarter_index:02d}",
            f"Quarter price {label}",
        )

    @property
    def native_value(self) -> float | None:
        """Return quarter price in PLN/kWh."""
        item = self._get_quarter_item()
        return item.price_pln_per_kwh if item else None

    def _get_quarter_item(self) -> QuarterPrice | None:
        """Return cached quarter item by index."""
        prices = self.coordinator.data.prices_today
        if self._quarter_index < len(prices):
            return prices[self._quarter_index]
        return None
