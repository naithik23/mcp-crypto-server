from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import Any, Dict
import json
import os

from server.exchange import ExchangeClient, ExchangeFetchError
from server.cache import Cache

router = APIRouter(prefix="/mcp", tags=["mcp"])

_client = ExchangeClient()
_cache = Cache(ttl=10)

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "mcp_manifest.json")


@router.get("/manifest.json")
async def manifest():
    if os.path.exists(MANIFEST_PATH):
        return FileResponse(MANIFEST_PATH, media_type="application/json")
    return JSONResponse(status_code=404, content={"error": "manifest not found"})


def _normalize_symbol_for_coingecko(s: str) -> str:
    mapping = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "DOGE": "dogecoin",
        "BNB": "binancecoin",
        "USDT": "tether"
    }
    s = s.strip()
    if "/" in s:
        s = s.split("/")[0]
    s_upper = s.upper()
    return mapping.get(s_upper, s.lower())


@router.post("/invoke")
async def invoke(req: Request):
    payload = await req.json()
    method = payload.get("method")
    params = payload.get("params", {})

    if not method:
        raise HTTPException(status_code=400, detail="missing method")

    try:
        if method == "get_price":
            symbol = params.get("symbol")
            if not symbol:
                raise HTTPException(status_code=400, detail="missing symbol param")

            cg_symbol = _normalize_symbol_for_coingecko(symbol)
            cached_key = f"mcp:price:{cg_symbol}"
            cached = _cache.get(cached_key)
            if cached is not None:
                return {"ok": True, "result": {"symbol": symbol, "price": cached, "cached": True}}

            price = await _client.fetch_price(cg_symbol)
            _cache.set(cached_key, price)
            return {"ok": True, "result": {"symbol": symbol, "price": price, "cached": False}}

        elif method == "get_history":
            symbol = params.get("symbol")
            days = int(params.get("days", 30))
            if not symbol:
                raise HTTPException(status_code=400, detail="missing symbol param")

            cg_symbol = _normalize_symbol_for_coingecko(symbol)
            history = await _client.fetch_history(cg_symbol, days)
            return {"ok": True, "result": {"symbol": symbol, "days": days, "history": history}}

        elif method == "supported":
            return {"ok": True, "result": {"supported": ["bitcoin", "ethereum", "solana", "dogecoin", "binancecoin"]}}

        else:
            raise HTTPException(status_code=404, detail=f"method '{method}' not found")

    except ExchangeFetchError as e:
        return JSONResponse(status_code=502, content={"ok": False, "error": {"message": str(e), "code": -2}})
    except HTTPException as he:
        raise he
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": {"message": str(e), "code": -1}})
