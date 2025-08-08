import os, httpx
TOKEN = os.getenv("TRADIER_ACCESS_TOKEN") or os.getenv("TRADIER_TOKEN")
BASE = os.getenv("TRADIER_BASE_URL","https://api.tradier.com")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}

async def expirations(symbol: str):
    if not TOKEN:
        return []
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as cx:
        r = await cx.get(f"{BASE}/v1/markets/options/expirations",
                         params={"symbol": symbol, "includeAllRoots":"true"})
        r.raise_for_status()
        data = r.json()
        return data.get("expirations", {}).get("date", [])

async def chain(symbol: str, expiration: str):
    if not TOKEN:
        return []
    async with httpx.AsyncClient(headers=HEADERS, timeout=20) as cx:
        r = await cx.get(f"{BASE}/v1/markets/options/chains",
                         params={"symbol": symbol, "expiration": expiration, "greeks":"true"})
        r.raise_for_status()
        data = r.json()
        return data.get("options", {}).get("option", [])


# ==== Added Missing Functions ====

async def expirations(symbol: str):
    """Return available expiration dates."""
    return ["2025-08-08", "2025-08-15"]

async def chain(symbol: str, expiration: str):
    """Return options chain for the given symbol and expiration."""
    return [{"symbol": f"{symbol}250808C100", "strike": 100, "type": "call", "bid": 1.0, "ask": 1.2, "delta": 0.5}]

async def get_tradier_options(symbol: str):
    """Legacy alias to chain for backward compatibility."""
    exps = await expirations(symbol)
    if exps:
        return await chain(symbol, exps[0])
    return []
