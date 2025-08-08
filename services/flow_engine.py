# Flow scoring engine
def score_flow(flow_data: dict, trade_type: str = "day"):
    score = 0
    tags = []
    if not flow_data or "chains" not in flow_data:
        return {"flow_score": 0, "flow_tags": ["no_data"]}
    calls = sum(1 for c in flow_data["chains"] if c["type"] == "call")
    puts = sum(1 for c in flow_data["chains"] if c["type"] == "put")
    ratio = calls / max(1, puts)
    if ratio > 2:
        score += 2; tags.append("bullish_ratio")
    elif ratio < 0.5:
        score -= 2; tags.append("bearish_ratio")
    return {"flow_score": score, "flow_tags": tags}


# ==== Added Missing Functions ====

async def get_flow_snapshot(symbol: str):
    """Fetch flow snapshot from Unusual Whales and calculate bias."""
    # TODO: Integrate real UW data
    return {
        "bullish_score": 60,
        "bearish_score": 40,
        "bias": "bullish"
    }
