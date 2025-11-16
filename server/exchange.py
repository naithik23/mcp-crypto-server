# server/exchange.py
import aiohttp
from datetime import datetime


class ExchangeFetchError(Exception):
    pass


# Ticker → CoinGecko mapping
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "DOGE": "dogecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOT": "polkadot",
}


def normalize_symbol(symbol: str):
    """Convert tickers (BTC, ETH) → CoinGecko IDs (bitcoin, ethereum)."""
    symbol = symbol.upper().replace("USDT", "").replace("/", "")

    if symbol in COINGECKO_MAP:
        return COINGECKO_MAP[symbol]

    # fallback
    return symbol.lower()


class ExchangeClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    async def fetch_price(self, symbol: str):
        cg_symbol = normalize_symbol(symbol)

        url = f"{self.BASE_URL}/simple/price?ids={cg_symbol}&vs_currencies=usd"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

                if cg_symbol not in data:
                    raise ExchangeFetchError(f"Failed to fetch price for {symbol}: Price not found")

                return data[cg_symbol]["usd"]

    async def fetch_history(self, symbol: str, days: int):
        cg_symbol = normalize_symbol(symbol)

        url = f"{self.BASE_URL}/coins/{cg_symbol}/market_chart?vs_currency=usd&days={days}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

                if "prices" not in data:
                    raise ExchangeFetchError(f"Failed to fetch history for {symbol}: History not found")

                history = [
                    {
                        "date": datetime.utcfromtimestamp(p[0] / 1000).strftime("%Y-%m-%d"),
                        "price": p[1]
                    }
                    for p in data["prices"]
                ]

                return history
