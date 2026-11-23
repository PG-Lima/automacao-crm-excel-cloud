from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


RATE_URL = "https://api.frankfurter.dev/v2/rate/BRL/USD"
RATE_SOURCE_NAME = "Frankfurter"
RATE_CACHE_SECONDS = 6 * 60 * 60  # Reference rates are refreshed a few times per business day.
REQUEST_TIMEOUT_SECONDS = 5


class ExchangeRateError(RuntimeError):
    """Raised when a reliable BRL/USD reference rate cannot be retrieved."""


@dataclass(frozen=True, slots=True)
class ExchangeRate:
    base: str
    quote: str
    rate: Decimal
    rate_date: date
    source: str = RATE_SOURCE_NAME
    source_url: str = RATE_URL


_cache_lock = threading.Lock()
_cached_rate: tuple[float, ExchangeRate] | None = None


def clear_exchange_rate_cache() -> None:
    """Clear the in-process rate cache. Intended mainly for tests."""
    global _cached_rate

    with _cache_lock:
        _cached_rate = None


def _fetch_brl_to_usd_rate() -> ExchangeRate:
    request = Request(
        RATE_URL,
        headers={"Accept": "application/json", "User-Agent": "crm-excel-cloud-demo/1.0"},
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"), parse_float=Decimal)
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExchangeRateError(
            "The BRL/USD reference rate could not be retrieved."
        ) from exc

    try:
        rate = Decimal(str(payload["rate"]))
        rate_date = date.fromisoformat(payload["date"])
        base = str(payload["base"]).upper()
        quote = str(payload["quote"]).upper()
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise ExchangeRateError(
            "The exchange-rate provider returned an invalid response."
        ) from exc

    if base != "BRL" or quote != "USD" or not rate.is_finite() or rate <= 0:
        raise ExchangeRateError(
            "The exchange-rate provider returned an invalid BRL/USD rate."
        )

    return ExchangeRate(
        base=base,
        quote=quote,
        rate=rate,
        rate_date=rate_date,
    )


def get_brl_to_usd_rate() -> ExchangeRate:
    """Return a cached daily reference rate for converting BRL amounts to USD."""
    global _cached_rate

    now = time.monotonic()

    with _cache_lock:
        if _cached_rate and now - _cached_rate[0] < RATE_CACHE_SECONDS:
            return _cached_rate[1]

    # Fetch outside the lock so a slow network request does not block readers.
    rate = _fetch_brl_to_usd_rate()

    with _cache_lock:
        _cached_rate = (time.monotonic(), rate)

    return rate


def convert_brl_to_usd(amount: int | float | Decimal, rate: Decimal) -> Decimal:
    """Convert a BRL amount to USD using an explicit reference rate."""
    try:
        brl_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("The BRL amount must be numeric.") from exc

    if not brl_amount.is_finite() or not rate.is_finite() or rate <= 0:
        raise ValueError("The amount and exchange rate must be finite; rate must be positive.")

    return (brl_amount * rate).quantize(Decimal("0.01"))
