import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


# pylint: disable=redefined-outer-name


@parametrize(
    "params",
    [
        ({"query": "", "provider": "fmp"}),
        (
            {
                "query": "vanguard",
                "provider": "tmx",
                "div_freq": "quarterly",
                "sort_by": "return_1y",
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_etf_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "adjustment": "unadjusted",
                "extended_hours": True,
                "provider": "alpha_vantage",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "15m",
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "SPY",
                "start_date": None,
                "end_date": None,
                "interval": "1m",
                "use_cache": False,
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
                "use_cache": False,
            }
        ),
        (
            {
                "provider": "fmp",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "timezone": "UTC",
                "source": "realtime",
                "start_time": None,
                "end_time": None,
                "provider": "intrinio",
                "symbol": "SPY",
                "start_date": "2023-06-01",
                "end_date": "2023-06-03",
                "interval": "1h",
            }
        ),
        (
            {
                "timezone": None,
                "source": "delayed",
                "start_time": None,
                "end_time": None,
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "sort": "desc",
                "limit": "49999",
                "adjustment": "unadjusted",
                "provider": "polygon",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-01-03",
                "interval": "1m",
                "extended_hours": False,
            }
        ),
        (
            {
                "sort": "desc",
                "limit": "49999",
                "adjustment": "splits_only",
                "provider": "polygon",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
                "extended_hours": False,
            }
        ),
        (
            {
                "extended_hours": False,
                "include_actions": False,
                "adjustment": "splits_and_dividends",
                "provider": "yfinance",
                "symbol": "SPY",
                "start_date": "2023-06-01",
                "end_date": "2023-06-03",
                "interval": "1h",
                "adjusted": True,
                "prepost": False,
            }
        ),
        (
            {
                "extended_hours": False,
                "include_actions": True,
                "adjustment": "splits_only",
                "provider": "yfinance",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
                "adjusted": False,
                "prepost": False,
            }
        ),
        (
            {
                "provider": "tiingo",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "provider": "tiingo",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1M",
            }
        ),
        (
            {
                "provider": "tradier",
                "symbol": "SPY",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1M",
                "extended_hours": False,
            }
        ),
        (
            {
                "provider": "tradier",
                "symbol": "SPY,DJIA",
                "start_date": None,
                "end_date": None,
                "interval": "15m",
                "extended_hours": False,
            }
        ),
        (
            {
                "provider": "tmx",
                "symbol": "SPY:US",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "interval": "1d",
                "adjustment": "splits_only",
            }
        ),
    ],
)
@pytest.mark.integration
def test_etf_historical(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "XIU", "provider": "tmx", "use_cache": False}),
        ({"symbol": "QQQ", "provider": "yfinance"}),
    ],
)
@pytest.mark.integration
def test_etf_info(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/info?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "XIU", "provider": "tmx", "use_cache": False}),
    ],
)
@pytest.mark.integration
def test_etf_sectors(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/sectors?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "QQQ", "cik": None, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_holdings_date(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/holdings_date?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "IOO",
                "date": "2023-03-31",
                "cik": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "VOO",
                "date": "2023-03-31",
                "cik": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "TQQQ",
                "date": None,
                "provider": "sec",
                "use_cache": False,
            }
        ),
        (
            {
                "symbol": "QQQ",
                "date": "2021-06-30",
                "provider": "sec",
                "use_cache": False,
            }
        ),
        (
            {
                "symbol": "XIU",
                "provider": "tmx",
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_etf_holdings(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/holdings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "SPY,VOO,QQQ,IWM,IWN,GOVT,JNK", "provider": "fmp"}),
        ({"symbol": "SPY,VOO,QQQ,IWM,IWN,GOVT,JNK", "provider": "finviz"}),
    ],
)
@pytest.mark.integration
def test_etf_price_performance(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/price_performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "XIU", "use_cache": False, "provider": "tmx"}),
    ],
)
@pytest.mark.integration
def test_etf_countries(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/countries?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_gainers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/discovery/gainers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_losers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/discovery/losers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_active(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/discovery/active?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "SPY", "provider": "fmp"}),
        ({"symbol": "QQQ", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_holdings_performance(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/holdings_performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "SPY,VOO,QQQ,IWM,IWN", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_equity_exposure(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/equity_exposure?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
