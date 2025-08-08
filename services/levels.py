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
