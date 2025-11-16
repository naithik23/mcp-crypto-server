# server/ccxt_client.py
import ccxt
import asyncio
from server.exchange import ExchangeFetchError


class CCXTClient:
    """
    Wrapper around CCXT to support major exchanges.
    Uses run_in_executor so blocking CCXT calls don't break the event loop.
    """

    # Exchanges that require API keys for public price data (disable them)
    UNSUPPORTED_EXCHANGES = ["okx"]

    def __init__(self, exchange_id="binance"):
        self.set_exchange(exchange_id)

    def set_exchange(self, exchange_id: str):
        exchange_id = exchange_id.lower()

        # block unsupported exchanges
        if exchange_id in self.UNSUPPORTED_EXCHANGES:
            raise ExchangeFetchError(
                f"Exchange '{exchange_id}' is disabled (requires API keys)."
            )

        # check if CCXT supports the exchange
        if exchange_id not in ccxt.exchanges:
            raise ExchangeFetchError(
                f"Exchange '{exchange_id}' is not supported by CCXT."
            )

        # instantiate exchange
        try:
            self.exchange = getattr(ccxt, exchange_id)()
            self.exchange_id = exchange_id
        except Exception as e:
            raise ExchangeFetchError(f"Failed to initialize exchange '{exchange_id}': {e}")

    async def fetch_price(self, symbol: str):
        """
        Fetch the latest price using CCXT fetch_ticker() in a separate thread.
        Example symbol: 'BTC/USDT'
        """
        loop = asyncio.get_event_loop()

        try:
            ticker = await loop.run_in_executor(
                None, self.exchange.fetch_ticker, symbol
            )

            last = ticker.get("last")
            if last is None:
                raise ExchangeFetchError(
                    f"No 'last' price available for {symbol} on {self.exchange_id}"
                )

            return last

        except Exception as e:
            raise ExchangeFetchError(
                f"CCXT fetch_price failed ({self.exchange_id} {symbol}): {e}"
            )

    async def fetch_history(self, symbol: str, timeframe="1d", limit=30):
        """
        Fetch OHLCV candles using CCXT fetch_ohlcv() in a thread.
        """
        loop = asyncio.get_event_loop()

        try:
            candles = await loop.run_in_executor(
                None, lambda: self.exchange.fetch_ohlcv(
                    symbol, timeframe=timeframe, limit=limit
                )
            )

            history = []
            for c in candles:
                history.append({
                    "timestamp": c[0],
                    "open": c[1],
                    "high": c[2],
                    "low": c[3],
                    "close": c[4],
                    "volume": c[5],
                })

            return history

        except Exception as e:
            raise ExchangeFetchError(
                f"CCXT fetch_history failed ({self.exchange_id} {symbol}): {e}"
            )
