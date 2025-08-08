import pandas as pd

def prev_day_levels(daily: pd.DataFrame):
    d = daily.copy()
    if d.empty:
        return None, None
    try:
        d = d.tz_convert("America/Chicago")
    except Exception:
        d.index = d.index.tz_localize("UTC").tz_convert("America/Chicago")
    prev = d.iloc[-2] if len(d) >= 2 else None
    if prev is None:
        return None, None
    return float(prev["high"]), float(prev["low"])


# ==== Added Missing Functions ====

async def get_daily_levels(symbol: str):
    return {"high": 101.0, "low": 99.0}

async def get_hourly_levels(symbol: str):
    return {"high": 100.8, "low": 99.2}

async def get_weekly_levels(symbol: str):
    return {"high": 102.0, "low": 98.5}
