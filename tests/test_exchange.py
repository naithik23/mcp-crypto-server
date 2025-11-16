import pytest
import pytest_asyncio
from server.exchange import ExchangeClient, ExchangeFetchError

@pytest_asyncio.fixture
async def client():
    return ExchangeClient()

# ----------------------------------------------------
# Test price fetch (mocked)
# ----------------------------------------------------
@pytest.mark.asyncio
async def test_fetch_price_success(monkeypatch, client):
    async def mock_fetch_price(self, symbol):
        return 12345.67

    monkeypatch.setattr(ExchangeClient, "fetch_price", mock_fetch_price)

    price = await client.fetch_price("BTC")
    assert price == 12345.67

@pytest.mark.asyncio
async def test_fetch_price_fail(monkeypatch, client):
    async def mock_fetch_price(self, symbol):
        raise ExchangeFetchError("symbol not found")

    monkeypatch.setattr(ExchangeClient, "fetch_price", mock_fetch_price)

    with pytest.raises(ExchangeFetchError):
        await client.fetch_price("BAD")

# ----------------------------------------------------
# Test historical fetch (mocked)
# ----------------------------------------------------
@pytest.mark.asyncio
async def test_fetch_history_success(monkeypatch, client):
    async def mock_history(self, symbol, days):
        return [
            {"date": "2024-01-01", "price": 100},
            {"date": "2024-01-02", "price": 105},
        ]

    monkeypatch.setattr(ExchangeClient, "fetch_history", mock_history)

    hist = await client.fetch_history("BTC", 2)
    assert len(hist) == 2
    assert hist[0]["price"] == 100

@pytest.mark.asyncio
async def test_fetch_history_fail(monkeypatch, client):
    async def mock_history(self, symbol, days):
        raise ExchangeFetchError("history missing")

    monkeypatch.setattr(ExchangeClient, "fetch_history", mock_history)

    with pytest.raises(ExchangeFetchError):
        await client.fetch_history("BTC", 30)
