# Trade planning with flow
from .features_snapshot import features_snapshot

async def plan_trade(symbol: str, trade_type: str = "day"):
    snap = await features_snapshot(symbol, trade_type)
    confluence = 5 + snap.get("flow_score", 0)
    return {
        "symbol": symbol,
        "bias": "Long" if confluence >= 5 else "Short",
        "confluence_score": confluence,
        "flow_tags": snap.get("flow_tags", [])
    }
