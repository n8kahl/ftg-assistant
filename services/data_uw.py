# Unusual Whales data fetcher for intraday and swing flow
import httpx, os, datetime

UW_API_KEY = os.getenv("UW_API_KEY")
UW_BASE = "https://api.unusualwhales.com"

async def fetch_flow(symbol: str, scope: str = "intraday"):
    endpoint = "/flow" if scope == "intraday" else "/flow/historical"
    params = {"symbol": symbol}
    headers = {"Authorization": f"Bearer {UW_API_KEY}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{UW_BASE}{endpoint}", params=params, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
