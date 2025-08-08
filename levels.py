# services/levels.py
from services.data_alpaca import get_agg
import pandas as pd

async def get_daily_levels(symbol: str, days_back: int = 5):
    df = await get_agg(symbol, "D")
    levels = []
    for _, row in df.tail(days_back).iterrows():
        levels.append({
            "high": float(row["high"]),
            "low": float(row["low"]),
            "midpoint": float((row["high"] + row["low"]) / 2),
            "close": float(row["close"])
        })
    return {"daily": levels}

async def get_hourly_levels(symbol: str, hours_back: int = 48):
    df = await get_agg(symbol, "1h")
    levels = []
    for _, row in df.tail(hours_back).iterrows():
        levels.append({
            "high": float(row["high"]),
            "low": float(row["low"]),
            "midpoint": float((row["high"] + row["low"]) / 2),
            "close": float(row["close"])
        })
    return {"hourly": levels}

async def get_weekly_levels(symbol: str, weeks_back: int = 6):
    df = await get_agg(symbol, "W")
    levels = []
    for _, row in df.tail(weeks_back).iterrows():
        levels.append({
            "high": float(row["high"]),
            "low": float(row["low"]),
            "midpoint": float((row["high"] + row["low"]) / 2),
            "close": float(row["close"])
        })
    return {"weekly": levels}
