# server/main.py
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from server.exchange import ExchangeClient
from server.cache import Cache
from server.ccxt_client import CCXTClient
from server.cmc_client import CoinMarketCapClient
from server.mcp_tool import router as mcp_router

# ----------------------------------------------------
# FASTAPI APP
# ----------------------------------------------------
app = FastAPI(title="Crypto MCP Server")

# Allow frontend / browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mcp_router)

# ----------------------------------------------------
# BACKEND CLIENTS
# ----------------------------------------------------
coingecko_client = ExchangeClient()
cache = Cache(ttl=10)   # 10-second cache

ccxt_client = CCXTClient("binance")
cmc_client = CoinMarketCapClient()

USE_CCXT = False   # disabled by default
USE_CMC = False    # disabled by default

# Logging setup
logger = logging.getLogger("CryptoMCP")
logging.basicConfig(level=logging.INFO)


# ----------------------------------------------------
# ROOT ENDPOINT
# ----------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Crypto MCP Server is Running ✔"}


# ----------------------------------------------------
# SWITCH EXCHANGE SOURCE
# ----------------------------------------------------
@app.get("/exchange/set/{exchange_id}")
async def set_exchange(exchange_id: str):
    """
    Switch API source:
    - CoinGecko (default)
    - CCXT (binance, kraken, coinbase, bybit…)
    - CoinMarketCap (cmc)
    """
    global USE_CCXT, USE_CMC

    exchange_id = exchange_id.lower()

    # enable CoinMarketCap
    if exchange_id == "cmc":
        USE_CCXT = False
        USE_CMC = True
        return {"source": "coinmarketcap", "message": "Now using CoinMarketCap API"}

    # enable CCXT exchange
    try:
        ccxt_client.set_exchange(exchange_id)
        USE_CCXT = True
        USE_CMC = False
        return {"source": "ccxt", "exchange": exchange_id}
    except Exception as e:
        USE_CCXT = False
        USE_CMC = False
        return {"error": str(e), "source": "coingecko-fallback"}


# ----------------------------------------------------
# PRICE ENDPOINT
# ----------------------------------------------------
@app.get("/price/{symbol}")
async def get_price(symbol: str):
    symbol = symbol.upper()

    # 1️⃣ CoinMarketCap mode
    if USE_CMC:
        try:
            price = await cmc_client.fetch_price(symbol)
            return {"symbol": symbol, "price": price, "source": "coinmarketcap"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"CMC error: {e}")

    # 2️⃣ CCXT mode
    if USE_CCXT:
        try:
            price = await ccxt_client.fetch_price(f"{symbol}/USDT")
            return {"symbol": symbol, "price": price, "source": f"ccxt-{ccxt_client.exchange_id}"}
        except Exception as e:
            logger.error(f"CCXT price error: {e}")

    # 3️⃣ CoinGecko fallback
    cached = cache.get(symbol)
    if cached:
        return {"symbol": symbol, "price": cached, "cached": True, "source": "coingecko"}

    try:
        price = await coingecko_client.fetch_price(symbol)
        if price is None:
            raise HTTPException(status_code=404, detail="Crypto not found")

        cache.set(symbol, price)
        return {"symbol": symbol, "price": price, "cached": False, "source": "coingecko"}

    except Exception as e:
        logger.error(f"Error in /price/{symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"internal error: Failed to fetch price for {symbol}")


# ----------------------------------------------------
# HISTORICAL DATA ENDPOINT
# ----------------------------------------------------
@app.get("/historical/{symbol}")
async def get_historical(symbol: str, days: int = 30):
    symbol = symbol.upper()

    # 1️⃣ CCXT Mode
    if USE_CCXT:
        try:
            history = await ccxt_client.fetch_history(f"{symbol}/USDT", timeframe="1d", limit=days)
            return {
                "symbol": symbol,
                "days": days,
                "history": history,
                "source": f"ccxt-{ccxt_client.exchange_id}"
            }
        except Exception as e:
            logger.error(f"CCXT history error: {e}")

    # 2️⃣ CoinMarketCap Mode (fallback to CoinGecko)
    if USE_CMC:
        try:
            # CoinMarketCap free tier has no historical → use CoinGecko instead
            history = await coingecko_client.fetch_history(symbol, days)
            return {
                "symbol": symbol,
                "days": days,
                "history": history,
                "source": "coingecko-fallback"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch history (CMC fallback): {e}")

    # 3️⃣ Default CoinGecko Mode
    try:
        history = await coingecko_client.fetch_history(symbol, days)
        if not history:
            raise HTTPException(status_code=404, detail="No history found")

        return {
            "symbol": symbol,
            "days": days,
            "history": history,
            "source": "coingecko"
        }

    except Exception as e:
        logger.error(f"Error in /historical/{symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"internal error: Failed to fetch history for {symbol}")

# ----------------------------------------------------
# UVICORN SERVER (DEV)
# ----------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("🚀 Crypto MCP Server running at: http://127.0.0.1:8000")
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)
