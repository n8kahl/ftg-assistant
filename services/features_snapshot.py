# Merged snapshot with flow data
from .data_uw import fetch_flow
from .flow_engine import score_flow

async def features_snapshot(symbol: str, trade_type: str = "day"):
    tech_data = {"symbol": symbol, "emas": {}, "vwap": {}, "momentum": {}, "levels": {}}
    flow_data = await fetch_flow(symbol, scope="intraday" if trade_type=="day" else "swing")
    scored_flow = score_flow(flow_data, trade_type=trade_type)
    tech_data.update(scored_flow)
    return tech_data
