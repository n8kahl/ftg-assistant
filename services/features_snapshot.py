# services/features_snapshot.py

from services.data_alpaca import get_alpaca_snapshot
from services.data_polygon import get_polygon_snapshot
from services.data_tradier import get_tradier_options
from services.features import build_indicators
from services.levels import get_daily_levels, get_hourly_levels, get_weekly_levels
from services.flow_engine import get_flow_snapshot
from services.options_picker import pick_options
from services.strategies import evaluate_trade
import logging

logger = logging.getLogger(__name__)

def build_features_snapshot(symbol: str) -> dict:
    snapshot = {"symbol": symbol}

    # --- Core market data ---
    try:
        alpaca_data = get_alpaca_snapshot(symbol)
        snapshot.update(alpaca_data)
    except Exception as e:
        logger.error(f"Alpaca snapshot failed for {symbol}: {e}")
        try:
            polygon_data = get_polygon_snapshot(symbol)
            snapshot.update(polygon_data)
        except Exception as e2:
            logger.error(f"Polygon snapshot failed for {symbol}: {e2}")
            snapshot["error"] = "API unavailable / data incomplete"
            return snapshot

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
