# services/features_snapshot.py
from services.data_alpaca import get_agg
from services.data_tradier import expirations, chain
from services.features import build_indicators
from services.levels import get_daily_levels, get_hourly_levels, get_weekly_levels
from services.flow_engine import get_flow_snapshot
from services.options_picker import pick_options
from services.strategies import generate_plan

async def build_features_snapshot(symbol: str) -> dict:
    snapshot = {"symbol": symbol}

    # Latest bar
    df5 = await get_agg(symbol, "5m")
    if df5.empty:
        snapshot["error"] = "API unavailable / data incomplete"
        return snapshot
    last = df5.iloc[-1]
    snapshot.update({
        "price": float(last["close"]),
        "high": float(last["high"]),
        "low": float(last["low"]),
        "open": float(last["open"]),
        "volume": float(last["volume"])
    })

    # Indicators
    snapshot.update(build_indicators(snapshot))

    # Levels
    snapshot["levels_daily"] = await get_daily_levels(symbol)
    snapshot["levels_hourly"] = await get_hourly_levels(symbol)
    snapshot["levels_weekly"] = await get_weekly_levels(symbol)

    # Options candidates
    exps = await expirations(symbol)
    opts = []
    if exps:
        chain_data = await chain(symbol, exps[0])
        opts = pick_options(chain_data)
    snapshot["options_candidates"] = opts

    # Flow data
    snapshot["flow_data"] = await get_flow_snapshot(symbol)

    # Strategy plan
    snapshot["plan"] = await generate_plan(snapshot)

    return snapshot
