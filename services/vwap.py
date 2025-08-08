import pandas as pd
from typing import Optional
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")

def session_open_ts(df_1m: pd.DataFrame) -> Optional[pd.Timestamp]:
    if df_1m.empty:
        return None
    idx = df_1m.index.tz_convert(CT)
    # Regular session open 08:30 CT
    open_ts = idx[idx.time >= pd.Timestamp('08:30', tz=CT).time()].min()
    return open_ts.tz_convert('UTC') if open_ts is not pd.NaT else None

def session_vwap(df_1m: pd.DataFrame) -> Optional[float]:
    """Session VWAP from regular session open to latest bar."""
    if df_1m.empty:
        return None
    so = session_open_ts(df_1m)
    if so is None:
        return None
    intr = df_1m[df_1m.index >= so]
    if intr.empty:
        return None
    tp = (intr['high'] + intr['low'] + intr['close']) / 3.0
    pv = tp * intr['volume'].clip(lower=0)
    cum_pv = pv.cumsum()
    cum_v = intr['volume'].clip(lower=0).cumsum().replace(0, pd.NA)
    vwap = (cum_pv / cum_v).iloc[-1]
    return float(vwap) if pd.notna(vwap) else None

def anchored_vwap(df_1m: pd.DataFrame, anchor_ts_utc: pd.Timestamp) -> Optional[float]:
    """Anchored VWAP from a UTC timestamp onward."""
    intr = df_1m[df_1m.index >= anchor_ts_utc]
    if intr.empty:
        return None
    tp = (intr['high'] + intr['low'] + intr['close']) / 3.0
    pv = tp * intr['volume'].clip(lower=0)
    cum_pv = pv.cumsum()
    cum_v = intr['volume'].clip(lower=0).cumsum().replace(0, pd.NA)
    vwap = (cum_pv / cum_v).iloc[-1]
    return float(vwap) if pd.notna(vwap) else None

def opening_range(df_1m: pd.DataFrame, minutes: int = 5):
    """Return Opening Range High/Low for the first N minutes after regular open."""
    if df_1m.empty:
        return None, None
    so = session_open_ts(df_1m)
    if so is None:
        return None, None
    end = so + pd.Timedelta(minutes=minutes)
    win = df_1m[(df_1m.index >= so) & (df_1m.index < end)]
    if win.empty:
        return None, None
    return float(win['high'].max()), float(win['low'].min())
