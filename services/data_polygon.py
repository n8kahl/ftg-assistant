import os, datetime as dt, asyncio
from dateutil.relativedelta import relativedelta
import httpx
import pandas as pd

API_KEY = os.getenv("POLYGON_API_KEY")
BASE = "https://api.polygon.io"

TF_MAP = {"1m": (1, "minute", 2), "5m": (5, "minute", 5), "15m": (15, "minute", 15), "1h": (1, "hour", 30), "D": (1, "day", 365)}

def _rng(days):
    end = dt.datetime.utcnow()
    start = end - dt.timedelta(days=days)
    return start.date().isoformat(), end.date().isoformat()

async def get_agg(symbol: str, tf: str, limit: int = 2000) -> pd.DataFrame:
    if not API_KEY:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"])
    mult, span, days = TF_MAP[tf]
    start, end = _rng(days)
    url = f"{BASE}/v2/aggs/ticker/{symbol}/range/{mult}/{span}/{start}/{end}"
    params = {"adjusted":"true","sort":"asc","limit":limit,"apiKey":API_KEY}
    async with httpx.AsyncClient(timeout=20.0) as cx:
        r = await cx.get(url, params=params)
        r.raise_for_status()
        data = r.json().get("results", []) or []
    if not data:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"])
    df = pd.DataFrame(data)
    df["ts"] = pd.to_datetime(df["t"], unit="ms", utc=True)
    df = df.rename(columns={"o":"open","h":"high","l":"low","c":"close","v":"volume"})
    df = df[{"ts","open","high","low","close","volume"}]
    return df.set_index("ts")
