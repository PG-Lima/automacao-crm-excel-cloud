from datetime import date
from decimal import Decimal
from urllib.error import URLError

import pytest

from crm_cloud_demo.currency import (
    ExchangeRate,
    ExchangeRateError,
    _fetch_brl_to_usd_rate,
    clear_exchange_rate_cache,
    convert_brl_to_usd,
    get_brl_to_usd_rate,
)


def test_brl_to_usd_conversion_returns_two_decimal_places():
    assert convert_brl_to_usd(8700.50, Decimal("0.20")) == Decimal("1740.10")
    assert convert_brl_to_usd(Decimal("1.025"), Decimal("1")) == Decimal("1.03")


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



def test_fetch_brl_to_usd_rate_parses_provider_response(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return (
                b'{"date":"2026-11-20","base":"BRL",'
                b'"quote":"USD","rate":0.2056}'
            )

    def fake_urlopen(request, timeout):
        assert request.full_url.endswith("/rate/brl/usd")
        assert timeout == 5
        return FakeResponse()

    monkeypatch.setattr("crm_cloud_demo.currency.urlopen", fake_urlopen)

    result = _fetch_brl_to_usd_rate()

    assert result.base == "BRL"
    assert result.quote == "USD"
    assert result.rate == Decimal("0.2056")
    assert result.rate_date == date(2026, 11, 20)


def test_fetch_brl_to_usd_rate_wraps_network_errors(monkeypatch):
    def fail_request(request, timeout):
        raise URLError("network unavailable")

    monkeypatch.setattr("crm_cloud_demo.currency.urlopen", fail_request)

    with pytest.raises(ExchangeRateError, match="could not be retrieved"):
        _fetch_brl_to_usd_rate()


@pytest.mark.parametrize(
    "payload",
    [
        b'{"date":"2026-11-20","base":"USD","quote":"BRL","rate":5.0}',
        b'{"date":"2026-11-20","base":"BRL","quote":"USD","rate":0}',
        b'{"date":"not-a-date","base":"BRL","quote":"USD","rate":0.2}',
        b'{"date":"2026-11-20","base":"BRL","quote":"USD"}',
        b"null",
    ],
)
def test_fetch_brl_to_usd_rate_rejects_invalid_provider_payloads(
    monkeypatch,
    payload,
):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return payload

    monkeypatch.setattr(
        "crm_cloud_demo.currency.urlopen",
        lambda request, timeout: FakeResponse(),
    )

    with pytest.raises(ExchangeRateError):
        _fetch_brl_to_usd_rate()


def test_conversion_rejects_non_finite_amounts_and_rates():
    with pytest.raises(ValueError):
        convert_brl_to_usd(Decimal("NaN"), Decimal("0.2"))

    with pytest.raises(ValueError):
        convert_brl_to_usd(100, Decimal("Infinity"))
