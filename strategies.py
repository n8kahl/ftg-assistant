# services/strategies.py
async def generate_plan(snapshot: dict) -> dict:
    symbol = snapshot.get("symbol")
    bias = None
    score = 0
    reasons = []

    # Trend
    ema9_15 = snapshot.get("ema9_15m")
    ema21_15 = snapshot.get("ema21_15m")
    ema50_15 = snapshot.get("ema50_15m")
    ema9_1h = snapshot.get("ema9_1h")
    ema21_1h = snapshot.get("ema21_1h")
    ema50_1h = snapshot.get("ema50_1h")
    if ema9_15 > ema21_15 > ema50_15 and ema9_1h > ema21_1h > ema50_1h:
        bias = "Long"
        score += 3
        reasons.append("15m & 1h EMA stack long")
    elif ema9_15 < ema21_15 < ema50_15 and ema9_1h < ema21_1h < ema50_1h:
        bias = "Short"
        score += 3
        reasons.append("15m & 1h EMA stack short")
    else:
        return {"decision": "no trade", "reason": "Trend misaligned"}

    # VWAP
    price = snapshot.get("price")
    vwap = snapshot.get("vwap")
    if bias == "Long" and price > vwap:
        score += 2
        reasons.append("Above session VWAP")
    elif bias == "Short" and price < vwap:
        score += 2
        reasons.append("Below session VWAP")
    else:
        return {"decision": "no trade", "reason": "VWAP misaligned"}

    # Momentum
    macd_hist = snapshot.get("macd_hist_5m")
    rsi14 = snapshot.get("rsi14_5m")
    if bias == "Long" and macd_hist > 0 and rsi14 > 50:
        score += 2
        reasons.append("MACD rising + RSI>50")
    elif bias == "Short" and macd_hist < 0 and rsi14 < 50:
        score += 2
        reasons.append("MACD falling + RSI<50")

    # Multi-timeframe levels
    targets = []
    for tf_key in ["hourly", "daily", "weekly"]:
        tf_levels = snapshot.get(f"levels_{tf_key}", {}).get(tf_key, [])
        for lvl in tf_levels:
            price_lvl = lvl["high"] if bias == "Long" else lvl["low"]
            if (bias == "Long" and price_lvl > price) or (bias == "Short" and price_lvl < price):
                targets.append((price_lvl, f"{tf_key.capitalize()} {'High' if bias == 'Long' else 'Low'}"))
    if bias == "Long":
        targets.sort(key=lambda x: x[0])
    else:
        targets.sort(key=lambda x: x[0], reverse=True)
    targets = targets[:2]

    if targets:
        dist_pct = abs((targets[0][0] - price) / price) * 100
        if dist_pct > 0.5:
            score += 2
        elif dist_pct < 0.3:
            score -= 2

    # Flow bias
    flow_bias = snapshot.get("flow_data", {}).get("bias")
    if flow_bias:
        if (flow_bias == "bullish" and bias == "Long") or (flow_bias == "bearish" and bias == "Short"):
            score += 1
        elif (flow_bias == "bullish" and bias == "Short") or (flow_bias == "bearish" and bias == "Long"):
            score -= 1

    return {
        "symbol": symbol,
        "bias": bias,
        "score": score,
        "decision": "trade" if score >= 7 else ("maybe" if score == 6 else "no trade"),
        "entry": price,
        "targets": targets,
        "reasons": reasons
    }
