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
