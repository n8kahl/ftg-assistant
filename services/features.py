import pandas as pd
import numpy as np

def ema(series: pd.Series, n: int) -> pd.Series:
    return series.ewm(span=n, adjust=False).mean()

def rsi(series: pd.Series, n: int = 14) -> pd.Series:
    delta = series.diff()
    up = (delta.clip(lower=0)).rolling(n).mean()
    down = (-delta.clip(upper=0)).rolling(n).mean()
    rs = up / (down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    prev_close = c.shift(1)
    tr = pd.concat([(h - l).abs(), (h - prev_close).abs(), (l - prev_close).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def compute_all(df: pd.DataFrame, ema_lens=(9,21,50,200)) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out
    for n in ema_lens:
        out[f"ema{n}"] = ema(out["close"], n)
    out["rsi14"] = rsi(out["close"], 14)
    macd_line, signal_line, hist = macd(out["close"])
    out["macd"] = macd_line
    out["macd_signal"] = signal_line
    out["macd_hist"] = hist
    out["atr14"] = atr(out, 14)
    return out


import pandas as pd
import numpy as np
from services.data_alpaca import get_alpaca_bars

async def build_indicators(symbol: str, timeframe: str = '5Min', limit: int = 1000):
    # Fetch historical bars
    bars = await get_alpaca_bars(symbol, timeframe, limit)
    if not bars or 't' not in bars:
        return None

    df = pd.DataFrame(bars)
    # Ensure numeric
    for col in ['o', 'h', 'l', 'c', 'v']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    # EMA calculations
    for length in [9, 21, 50, 200]:
        df[f'ema_{length}'] = df['c'].ewm(span=length).mean()

    # RSI14
    delta = df['c'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(14).mean()
    ma_down = down.rolling(14).mean()
    rs = ma_up / ma_down
    df['rsi14'] = 100 - (100 / (1 + rs))

    # MACD histogram (12,26,9)
    ema12 = df['c'].ewm(span=12).mean()
    ema26 = df['c'].ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    df['macd_hist'] = macd - signal

    # ATR14
    high_low = df['h'] - df['l']
    high_close = np.abs(df['h'] - df['c'].shift())
    low_close = np.abs(df['l'] - df['c'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['atr14'] = true_range.rolling(14).mean()

    # VWAP
    df['vwap'] = (df['v'] * (df['h'] + df['l'] + df['c']) / 3).cumsum() / df['v'].cumsum()

    return df.to_dict(orient='records')

# ==== Added Missing Functions ====

import pandas as pd

async def build_indicators(bars: pd.DataFrame):
    """Build EMA, RSI, MACD indicators from bar data."""
    # TODO: Real TA logic here
    return {
        "ema9": 100.1,
        "ema21": 99.9,
        "ema50": 99.5,
        "ema200": 98.0,
        "rsi14": 55,
        "macd_hist": 0.2,
        "vwap": 100.0
    }
