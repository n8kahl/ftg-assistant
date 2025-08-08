# services/flow_engine.py
from services.data_uw import fetch_flow

async def get_flow_snapshot(symbol: str, lookback_minutes: int = 60):
    flow_data = await fetch_flow(symbol, scope="intraday")
    if not flow_data or "chains" not in flow_data:
        return {"bias": "neutral", "call_premium": 0, "put_premium": 0, "notable_trades": []}

    calls = [c for c in flow_data["chains"] if c["type"] == "call"]
    puts = [p for p in flow_data["chains"] if p["type"] == "put"]

    total_call_prem = sum(float(c.get("premium", 0)) for c in calls)
    total_put_prem = sum(float(p.get("premium", 0)) for p in puts)

    bias = "neutral"
    if total_call_prem >= 500000 and total_call_prem >= 2 * total_put_prem:
        bias = "bullish"
    elif total_put_prem >= 500000 and total_put_prem >= 2 * total_call_prem:
        bias = "bearish"

    notable_trades = []
    for c in calls + puts:
        oi = float(c.get("open_interest", 0))
        size = float(c.get("size", 0))
        if oi > 0 and size / oi >= 0.1:
            notable_trades.append(c)

    return {
        "bias": bias,
        "call_premium": total_call_prem,
        "put_premium": total_put_prem,
        "notable_trades": notable_trades
    }
