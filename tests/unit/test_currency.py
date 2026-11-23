from datetime import date
from decimal import Decimal

import pytest

from crm_cloud_demo.currency import (
    ExchangeRate,
    clear_exchange_rate_cache,
    convert_brl_to_usd,
    get_brl_to_usd_rate,
)


def test_brl_to_usd_conversion_returns_two_decimal_places():
    assert convert_brl_to_usd(8700.50, Decimal("0.20")) == Decimal("1740.10")


@pytest.mark.parametrize("rate", [Decimal("0"), Decimal("-0.1")])
def test_conversion_rejects_non_positive_exchange_rates(rate: Decimal):
    with pytest.raises(ValueError):
        convert_brl_to_usd(100, rate)


def test_exchange_rate_is_cached(monkeypatch):
    clear_exchange_rate_cache()
    calls = 0
    expected = ExchangeRate(
        base="BRL",
        quote="USD",
        rate=Decimal("0.20"),
        rate_date=date(2026, 11, 22),
    )

    def fake_fetch():
        nonlocal calls
        calls += 1
        return expected

    monkeypatch.setattr("crm_cloud_demo.currency._fetch_brl_to_usd_rate", fake_fetch)

    assert get_brl_to_usd_rate() == expected
    assert get_brl_to_usd_rate() == expected
    assert calls == 1

    clear_exchange_rate_cache()
