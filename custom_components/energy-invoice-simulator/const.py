"""Constants for the Energy Bridge integration."""

from __future__ import annotations

DOMAIN = "invoice_simulator"
MANUFACTURER = "dlepcz"

CONF_IMPORT_SENSOR = "import_sensor"
CONF_EXPORT_SENSOR = "export_sensor"

DEFAULT_NAME = "Energy Invoice Simulator"
COORDINATOR_UPDATE_INTERVAL_SECONDS = 30

API_URL = "https://api.raporty.pse.pl/api/rce-pln"

COORDINATOR_NAME = "pse_rce_coordinator"

SENSOR_KEY_CURRENT_PRICE = "current_price"
SENSOR_KEY_NEXT_PRICE = "next_price"
SENSOR_KEY_MIN_PRICE_TODAY = "min_price_today"
SENSOR_KEY_MAX_PRICE_TODAY = "max_price_today"
SENSOR_KEY_AVERAGE_PRICE_TODAY = "average_price_today"
CURRENCY_PLN = "PLN"


INVOICE_INPUT_NUMBERS: dict[str, dict] = {
    "deposit": {
        "name": "Depozyt prosumencki (PLN)",
        "min": 0,
        "max": 100000,
        "step": 0.01,
        "unit_of_measurement": "PLN",
        "mode": "box",
    },
    "subscription_fee": {
        "name": "Opłata abonamentowa (PLN/month)",
        "initial": 0.74,
        "min": 0,
        "max": 1000,
        "step": 0.01,
        "unit_of_measurement": "PLN/month",
        "mode": "box",
    },
    "fixed_distribution_fee": {
        "name": "Opłata sieciowa stała (PLN/month)",
        "initial": 36.35,
        "min": 0,
        "max": 1000,
        "step": 0.01,
        "unit_of_measurement": "PLN/month",
        "mode": "box",
    },
    "variable_distribution_fee_nighttime": {
        "name": "Opłata sieciowa zmienna nocna (PLN/kWh)",
        "initial": 0.0851,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "box",
    },
    "variable_distribution_fee_daytime": {
        "name": "Opłata sieciowa zmienna dzienna (PLN/kWh)",
        "initial": 0.4017,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "box",
    },
    "quality_fee": {
        "name": "Opłata jakościowa (PLN/kWh)",
        "initial": 0.0331,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "box",
    },
    "res_fee": {
        "name": "Opłata OZE (PLN/kWh)",
        "initial": 0.0073,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "box",
    },
    "cogeneration_fee": {
        "name": "Opłata kogeneracyjna (PLN/kWh)",
        "initial": 0.0030,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "box",
    },
    "transition_fee": {
        "name": "Opłata przejściowa (PLN/month)",
        "initial": 0.0,
        "min": 0,
        "max": 1000,
        "step": 0.01,
        "unit_of_measurement": "PLN/month",
        "mode": "box",
    },
    "capacity_fee": {
        "name": "Opłata mocowa (PLN/month)",
        "initial": 24.05,
        "min": 0,
        "max": 1000,
        "step": 0.01,
        "unit_of_measurement": "PLN/month",
        "mode": "box",
    },
    "active_energy_fee_daytime": {
        "name": "Opłata energia czynna dzienna (PLN/kWh)",
        "initial": 0.8527,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "box",
    },
    "active_energy_fee_daytime_excise_duty": {
        "name": "Opłata energia czynna dzienna akcyza (PLN/kWh)",
        "initial": 0.005,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "box",
    },
    "active_energy_fee_nighttime": {
        "name": "Opłata energia czynna nocna (PLN/kWh)",
        "initial": 0.5532,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "box",
    },
    "active_energy_fee_nighttime_excise_duty": {
        "name": "Opłata energia czynna nocna akcyza (PLN/kWh)",
        "initial": 0.005,
        "min": 0,
        "max": 10,
        "step": 0.0001,
        "unit_of_measurement": "PLN/kWh",
        "mode": "bosx",
    },
}
