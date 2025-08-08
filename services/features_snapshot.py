# services/features_snapshot.py

import asyncio
import logging
from services.data_alpaca import get_agg as get_alpaca_agg
from services.data_polygon import get_agg as get_polygon_agg
from services.data_tradier import get_tradier_options
from services.features import build_indicators
from services.levels import get_daily_levels, get_hourly_levels, get_weekly_levels
from services.flow_engine import get_flow_snapshot
from services.options_picker import pick_options
from services.strategies import evaluate_trade

logger = logging.getLogger(__name__)

def _latest_bar_to_dict(df):
    """Convert the last row of a DataFrame into snapshot fields."""
    if df is None or df.empty:
        return {}
    last = df.iloc[-1]
    return {
        "price": float(last.get("close", 0)),
        "high": float(last.get("high", 0)),
        "low": float(last.get("low", 0)),
        "open": float(last.get("open", 0)),
        "volume": float(last.get("volume", 0)),
        "timestamp": str(last.name) if hasattr(last, "name") else None
    }

def _get_latest_bar(symbol: str, tf: str = "5m"):
    """Try Alpaca first, fallback to Polygon."""
    try:
        df = asyncio.run(get_alpaca_agg(symbol, tf, limit=1))
        snap = _latest_bar_to_dict(df)
        if snap.get("price"):
            return snap
    except Exception as e:
        logger.warning(f"Alpaca agg failed for {symbol}: {e}")

    try:
        df = asyncio.run(get_polygon_agg(symbol, tf, limit=1))
        snap = _latest_bar_to_dict(df)
        if snap.get("price"):
            return snap
    except Exception as e:
        logger.error(f"Polygon agg failed for {symbol}: {e}")

    return {}

def build_features_snapshot(symbol: str) -> dict:
    snapshot = {"symbol": symbol}

    # --- Core latest bar ---
    latest_bar = _get_latest_bar(symbol, "5m")
    if not latest_bar:
        snapshot["error"] = "API unavailable / data incomplete"
        return snapshot
    snapshot.update(latest_bar)

    # --- Indicators ---
    try:
        indicators = build_indicators(snapshot)
        snapshot.update(indicators)
    except Exception as e:
        logger.error(f"Indicator build failed for {symbol}: {e}")

    # --- Levels: Hourly, Daily, Weekly ---
    try:
        snapshot["levels_daily"] = get_daily_levels(symbol)
        snapshot["levels_hourly"] = get_hourly_levels(symbol)
        snapshot["levels_weekly"] = get_weekly_levels(symbol)
    except Exception as e:
        logger.error(f"Level calc failed for {symbol}: {e}")
        snapshot["levels_daily"] = {}
        snapshot["levels_hourly"] = {}
        snapshot["levels_weekly"] = {}

    # --- Options candidates ---
    try:
        options_data = get_tradier_options(symbol)
        snapshot["options_candidates"] = pick_options(options_data)
    except Exception as e:
        logger.error(f"Options fetch failed for {symbol}: {e}")
        snapshot["options_candidates"] = []

    # --- Unusual Whales Flow ---
    try:
        flow_data = get_flow_snapshot(symbol)
        snapshot["flow_data"] = flow_data
    except Exception as e:
        logger.error(f"Flow fetch failed for {symbol}: {e}")
        snapshot["flow_data"] = {}

    # --- Strategy evaluation ---
    try:
        plan = evaluate_trade(snapshot)
        snapshot["plan"] = plan
    except Exception as e:
        logger.error(f"Strategy evaluation failed for {symbol}: {e}")
        snapshot["plan"] = {"error": str(e)}

    return snapshot
