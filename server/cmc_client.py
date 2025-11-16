# server/cmc_client.py
import os
import aiohttp
from dotenv import load_dotenv
from server.exchange import ExchangeFetchError

load_dotenv()  # load .env file

class CoinMarketCapClient:
    BASE_URL = "https://pro-api.coinmarketcap.com/v1"

    def __init__(self):
        self.api_key = os.getenv("CMC_API_KEY")
        if not self.api_key:
            raise ExchangeFetchError("CoinMarketCap API key is missing. Add CMC_API_KEY in .env")

    async def fetch_price(self, symbol: str):
        """
        Fetch real-time crypto price from CoinMarketCap.
        """
        url = f"{self.BASE_URL}/cryptocurrency/quotes/latest"

        headers = {"X-CMC_PRO_API_KEY": self.api_key}
        params = {"symbol": symbol.upper()}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                data = await resp.json()

                if "data" not in data or symbol.upper() not in data["data"]:
                    raise ExchangeFetchError(f"Price not found for {symbol}")

                return data["data"][symbol.upper()]["quote"]["USD"]["price"]

    async def fetch_history(self, symbol: str, days: int = 30):
        """
        CMC does not give historical candles in free tier.
        We simulate by returning last 'days' daily snapshots.
        """
        url = f"{self.BASE_URL}/cryptocurrency/quotes/historical"

        headers = {"X-CMC_PRO_API_KEY": self.api_key}
        params = {
            "symbol": symbol.upper(),
            "count": days,
            "interval": "daily"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                data = await resp.json()

                if "data" not in data or "quotes" not in data["data"]:
                    raise ExchangeFetchError(f"History not found for {symbol}")

                history = []
                for q in data["data"]["quotes"]:
                    history.append({
                        "timestamp": q["timestamp"],
                        "open": q["quote"]["USD"]["open"],
                        "high": q["quote"]["USD"]["high"],
                        "low": q["quote"]["USD"]["low"],
                        "close": q["quote"]["USD"]["close"],
                        "volume": q["quote"]["USD"]["volume"]
                    })

                return history
