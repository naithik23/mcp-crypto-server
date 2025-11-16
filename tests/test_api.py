# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

# ----------------------------------------------------
# Root endpoint
# ----------------------------------------------------
def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()

# ----------------------------------------------------
# MCP invoke endpoint
# ----------------------------------------------------
def test_mcp_invoke_missing_method():
    r = client.post("/mcp/invoke", json={"params": {}})
    assert r.status_code == 400

# ----------------------------------------------------
# Exchange switching
# ----------------------------------------------------
def test_set_exchange():
    r = client.get("/exchange/set/binance")
    assert r.status_code == 200
    assert r.json()["ccxt_enabled"] is True

# ----------------------------------------------------
# Price endpoint (mocked, CCXT disabled)
# ----------------------------------------------------
def test_price_endpoint_mock(monkeypatch):
    # Disable CCXT so that CoinGecko mock is used
    from server import main
    main.USE_CCXT = False

    # Mock function with self included
    async def fake_price(self, symbol):
        return 999.99

    from server.exchange import ExchangeClient
    monkeypatch.setattr(ExchangeClient, "fetch_price", fake_price)

    r = client.get("/price/BTC")
    assert r.status_code == 200
    assert r.json()["price"] == 999.99

# ----------------------------------------------------
# Historical endpoint (mocked)
# ----------------------------------------------------
def test_history_endpoint_mock(monkeypatch):
    async def fake_hist(self, symbol, days):
        return [{"date": "2024-01-01", "price": 50000}]

    from server.exchange import ExchangeClient
    monkeypatch.setattr(ExchangeClient, "fetch_history", fake_hist)

    r = client.get("/historical/BTC?days=1")
    assert r.status_code == 200
    assert len(r.json()["history"]) == 1
    assert r.json()["history"][0]["price"] == 50000
