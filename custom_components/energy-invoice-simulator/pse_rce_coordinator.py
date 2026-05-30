from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import API_URL, COORDINATOR_NAME, DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class QuarterPrice:
    """Single quarter-hour price item."""

    period: str
    start: datetime
    end: datetime
    price_pln_per_mwh: float
    price_pln_per_kwh: float
    dtime: str
    business_date: str
    publication_ts: str


@dataclass(slots=True)
class PseRceData:
    """Normalized coordinator payload."""

    business_date: str
    publication_ts: str | None
    current_item: QuarterPrice | None
    next_item: QuarterPrice | None
    min_price_today: float | None
    max_price_today: float | None
    average_price_today: float | None
    prices_today: list[QuarterPrice]


class PseRceDataUpdateCoordinator(DataUpdateCoordinator[PseRceData]):
    """Coordinator to fetch and normalize PSE RCE data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=COORDINATOR_NAME,
            update_interval=timedelta(hours=1),
        )
        self._entry = entry
        self._session = async_get_clientsession(hass)
        self._cached_business_date: str | None = None
        self._cached_prices_today: list[QuarterPrice] = []
        self._cached_publication_ts: str | None = None

        self._unsub_quarter: CALLBACK_TYPE | None = None
        self._unsub_midnight: CALLBACK_TYPE | None = None
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, "pse_rce")},
            name="Energy Invoice Simulator",
            model="Energy Invoice Simulator",
            entry_type=DeviceEntryType.SERVICE,
            manufacturer=MANUFACTURER,
        )

    async def async_start_listeners(self) -> None:
        """Start time-based listeners."""
        if self._unsub_quarter is None:
            self._unsub_quarter = async_track_time_change(
                self.hass,
                self._async_quarter_refresh,
                minute=[0, 15, 30, 45],
                second=0,
            )

        if self._unsub_midnight is None:
            self._unsub_midnight = async_track_time_change(
                self.hass,
                self._async_midnight_refresh,
                hour=0,
                minute=0,
                second=5,
            )

    async def async_stop_listeners(self) -> None:
        """Stop time-based listeners."""
        if self._unsub_quarter is not None:
            self._unsub_quarter()
            self._unsub_quarter = None

        if self._unsub_midnight is not None:
            self._unsub_midnight()
            self._unsub_midnight = None

    @callback
    def _async_quarter_refresh(self, now: datetime) -> None:
        """Refresh entities from cached day data every quarter."""
        if not self._cached_business_date or not self._cached_prices_today:
            return

        self.async_set_updated_data(
            self._build_payload_from_cache(self._cached_business_date)
        )

    @callback
    def _async_midnight_refresh(self, now: datetime) -> None:
        """Force refresh after midnight."""
        _LOGGER.debug("Midnight reached, clearing PSE cache and requesting refresh")
        self._cached_business_date = None
        self._cached_prices_today = []
        self._cached_publication_ts = None
        self.hass.async_create_task(self.async_request_refresh())

    async def _async_update_data(self) -> PseRceData:
        """Fetch data only when needed, otherwise reuse cached day data."""
        today_iso = dt_util.now().date().isoformat()

        if self._cached_business_date != today_iso or not self._cached_prices_today:
            await self._fetch_prices_for_day(today_iso)

        return self._build_payload_from_cache(today_iso)

    async def _fetch_prices_for_day(self, business_date: str) -> None:
        """Fetch prices for a given day from PSE API."""
        params = {
            "$filter": f"business_date eq '{business_date}'",
            "$first": "1000",
        }

        try:
            async with self._session.get(API_URL, params=params) as response:
                response.raise_for_status()
                payload: dict[str, Any] = await response.json()
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch PSE RCE data: {err}") from err

        raw_items = payload.get("value")
        if not isinstance(raw_items, list):
            raise UpdateFailed("Unexpected API response format: missing 'value' list")

        todays_items = [
            item
            for item in raw_items
            if isinstance(item, dict) and item.get("business_date") == business_date
        ]

        if not todays_items:
            raise UpdateFailed(f"No PSE RCE data available for day: {business_date}")

        parsed_items: list[QuarterPrice] = []
        for item in todays_items:
            try:
                parsed_items.append(self._parse_item(item))
            except Exception as err:
                _LOGGER.exception("Failed to parse PSE item: %s", item)
                raise UpdateFailed(f"Failed to parse PSE item: {err}") from err

        parsed_items.sort(key=lambda item: item.start)

        self._cached_business_date = business_date
        self._cached_prices_today = parsed_items
        self._cached_publication_ts = (
            parsed_items[0].publication_ts if parsed_items else None
        )

        _LOGGER.debug(
            "Fetched %s PSE RCE periods for %s",
            len(parsed_items),
            business_date,
        )

    def _build_payload_from_cache(self, business_date: str) -> PseRceData:
        """Build current payload from cached day data."""
        now_local = dt_util.now()
        current_item, current_index = self._find_current_item(
            self._cached_prices_today, now_local
        )

        next_item = None
        if current_index is not None and current_index + 1 < len(
            self._cached_prices_today
        ):
            next_item = self._cached_prices_today[current_index + 1]

        prices_kwh = [item.price_pln_per_kwh for item in self._cached_prices_today]

        return PseRceData(
            business_date=business_date,
            publication_ts=self._cached_publication_ts,
            current_item=current_item,
            next_item=next_item,
            min_price_today=min(prices_kwh) if prices_kwh else None,
            max_price_today=max(prices_kwh) if prices_kwh else None,
            average_price_today=(sum(prices_kwh) / len(prices_kwh))
            if prices_kwh
            else None,
            prices_today=self._cached_prices_today,
        )

    def _parse_item(self, item: dict[str, Any]) -> QuarterPrice:
        """Parse a single API item into a normalized dataclass.

        PSE returns `dtime` as the END of the quarter, which correctly handles
        the final period `23:45 - 24:00`.
        """
        business_date_str = str(item["business_date"])
        period = str(item["period"])
        price_pln_per_mwh = float(item["rce_pln"])
        price_pln_per_kwh = price_pln_per_mwh / 1000.0
        dtime_str = str(item["dtime"])
        publication_ts = str(item.get("publication_ts", ""))

        tz = dt_util.get_time_zone(self.hass.config.time_zone)
        naive_end = datetime.strptime(dtime_str, "%Y-%m-%d %H:%M:%S")
        end_dt = naive_end.replace(tzinfo=tz)
        start_dt = end_dt - timedelta(minutes=15)

        return QuarterPrice(
            period=period,
            start=start_dt,
            end=end_dt,
            price_pln_per_mwh=price_pln_per_mwh,
            price_pln_per_kwh=price_pln_per_kwh,
            dtime=dtime_str,
            business_date=business_date_str,
            publication_ts=publication_ts,
        )

    @staticmethod
    def _find_current_item(
        items: list[QuarterPrice], now_local: datetime
    ) -> tuple[QuarterPrice | None, int | None]:
        """Find the quarter matching current local time."""
        for index, item in enumerate(items):
            if item.start <= now_local < item.end:
                return item, index

        started = [
            (index, item) for index, item in enumerate(items) if item.start <= now_local
        ]
        if started:
            index, item = started[-1]
            return item, index

        if items:
            return items[0], 0

        return None, None
