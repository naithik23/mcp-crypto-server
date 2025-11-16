import ccxt
import asyncio

class ExchangeFetchError(Exception):
    pass


class ExchangeClient:
    def __init__(self, exchange_id: str):
        try:
            self.exchange = getattr(ccxt, exchange_id)()
        except Exception:
            raise ExchangeFetchError(f"Exchange '{exchange_id}' not supported")

    async def fetch_price(self, symbol: str):
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, self.exchange.fetch_ticker, symbol)

            if "last" not in ticker:
                raise ExchangeFetchError("Price not found")

            return ticker["last"]

        except Exception as e:
            raise ExchangeFetchError(str(e))

    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100):
        try:
            loop = asyncio.get_event_loop()
            ohlcv = await loop.run_in_executor(
                None,
                lambda: self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            )
            return ohlcv

        except Exception as e:
            raise ExchangeFetchError(str(e))

    async def fetch_history(self, symbol: str, timeframe: str = "1h", limit: int = 100):
        try:
            raw = await self.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

            history = []
            for candle in raw:
                history.append({
                    "timestamp": candle[0],
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                })

            return history

        except Exception as e:
            raise ExchangeFetchError(f"Failed to fetch historical data: {e}")
