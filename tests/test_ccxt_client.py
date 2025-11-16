import pytest
import pytest_asyncio
from server.ccxt_client import CCXTClient
from server.exchange import ExchangeFetchError

# ----------------------------------------------------
# Test setting exchange
# ----------------------------------------------------
def test_set_exchange_valid():
    c = CCXTClient("binance")
    assert c.exchange_id == "binance"

def test_set_exchange_invalid():
    c = CCXTClient("binance")
    with pytest.raises(ExchangeFetchError):
        c.set_exchange("invalid_exchange_xyz")

# ----------------------------------------------------
# Mocked CCXT price fetch
# ----------------------------------------------------
@pytest.mark.asyncio
async def test_fetch_price_mock(monkeypatch):
    c = CCXTClient("binance")

    async def mock_price(self, symbol):
        return 555.55

    monkeypatch.setattr(CCXTClient, "fetch_price", mock_price)

    price = await c.fetch_price("BTC/USDT")
    assert price == 555.55

@pytest.mark.asyncio
async def test_fetch_price_fail(monkeypatch):
    c = CCXTClient("binance")

    async def mock_error(self, symbol):
        raise ExchangeFetchError("price error")

    monkeypatch.setattr(CCXTClient, "fetch_price", mock_error)

    with pytest.raises(ExchangeFetchError):
        await c.fetch_price("BTC/USDT")

# ----------------------------------------------------
# Mock OHLCV history
# ----------------------------------------------------
@pytest.mark.asyncio
async def test_fetch_history_mock(monkeypatch):
    c = CCXTClient("binance")

    async def mock_hist(self, symbol, timeframe="1d", limit=3):
        return [
            {"timestamp": 1, "open": 10, "high": 12, "low": 9, "close": 11, "volume": 100},
            {"timestamp": 2, "open": 11, "high": 13, "low": 10, "close": 12, "volume": 120},
        ]

    monkeypatch.setattr(CCXTClient, "fetch_history", mock_hist)

    data = await c.fetch_history("BTC/USDT", limit=2)
    assert len(data) == 2
    assert data[0]["open"] == 10

@pytest.mark.asyncio
async def test_fetch_history_fail(monkeypatch):
    c = CCXTClient("binance")

    async def mock_error(self, symbol, timeframe="1d", limit=3):
        raise ExchangeFetchError("history error")

    monkeypatch.setattr(CCXTClient, "fetch_history", mock_error)

    with pytest.raises(ExchangeFetchError):
        await c.fetch_history("BTC/USDT")
