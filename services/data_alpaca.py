import os, datetime as dt
import httpx
import pandas as pd

# Accept underscore (correct) OR hyphen (just in case)
KEY = os.getenv("APCA_API_KEY_ID") or os.getenv("APCA-API-KEY-ID")
SECRET = os.getenv("APCA_API_SECRET_KEY") or os.getenv("APCA-API-SECRET-KEY")
FEED = os.getenv("ALPACA_FEED", "iex")  # iex or sip
BASE = "https://data.alpaca.markets"

TF_MAP = {"1m": ("1Min", 2), "5m": ("5Min", 5), "15m": ("15Min", 15), "1h": ("1Hour", 30), "D": ("1Day", 365)}

def _rng(days):
    end = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    start = end - dt.timedelta(days=days)
    to_iso = lambda d: d.isoformat().replace("+00:00","Z")
    return to_iso(start), to_iso(end)

async def get_agg(symbol: str, tf: str, limit: int = 2000) -> pd.DataFrame:
    if not KEY or not SECRET:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"]).set_index("ts")
    tf_api, days = TF_MAP[tf]
    start, end = _rng(days)
    url = f"{BASE}/v2/stocks/bars"
    params = {"symbols": symbol, "timeframe": tf_api, "limit": min(limit, 10000),
              "start": start, "end": end, "feed": FEED, "adjustment": "all"}
    headers = {"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SECRET}
    async with httpx.AsyncClient(timeout=20.0) as cx:
        r = await cx.get(url, params=params, headers=headers)
        r.raise_for_status()
        data = r.json().get("bars", {}).get(symbol, [])
    if not data:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"]).set_index("ts")
    df = pd.DataFrame(data)
    df["ts"] = pd.to_datetime(df["t"], utc=True)
    df = df.rename(columns={"o":"open","h":"high","l":"low","c":"close","v":"volume"})
    return df[["ts","open","high","low","close","volume"]].set_index("ts")
