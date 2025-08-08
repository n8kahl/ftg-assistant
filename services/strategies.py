# services/strategies.py

def find_targets_from_levels(entry_price: float, bias: str, levels_dicts: dict):
    """Select T1/T2 from hourly, daily, weekly levels in trade direction."""
    all_levels = []
    for timeframe in ["hourly", "daily", "weekly"]:
        if timeframe in levels_dicts:
            for lvl in levels_dicts[timeframe]:
                if bias == "Long":
                    price = lvl.get("high")
                    if price and price > entry_price:
                        all_levels.append((price, f"{timeframe.capitalize()} High"))
                else:
                    price = lvl.get("low")
                    if price and price < entry_price:
                        all_levels.append((price, f"{timeframe.capitalize()} Low"))
    if bias == "Long":
        all_levels.sort(key=lambda x: x[0])
    else:
        all_levels.sort(key=lambda x: x[0], reverse=True)
    return all_levels[:2]

def evaluate_trade(snapshot: dict) -> dict:
    symbol = snapshot.get("symbol")
    bias = None
    score = 0
    reasons = []

    # --- Trend ---
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

    # --- VWAP ---
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

    # --- Momentum ---
    macd_hist = snapshot.get("macd_hist_5m")
    rsi14 = snapshot.get("rsi14_5m")
    if bias == "Long" and macd_hist > 0 and rsi14 > 50:
        score += 2
        reasons.append("MACD rising + RSI>50")
    elif bias == "Short" and macd_hist < 0 and rsi14 < 50:
        score += 2
        reasons.append("MACD falling + RSI<50")
    else:
        reasons.append("Momentum not aligned")

    # --- Multi-timeframe levels ---
    targets = find_targets_from_levels(price, bias, {
        "hourly": snapshot.get("levels_hourly", {}).get("hourly", []),
        "daily": snapshot.get("levels_daily", {}).get("daily", []),
        "weekly": snapshot.get("levels_weekly", {}).get("weekly", [])
    })
    if targets:
        distance_pct = abs((targets[0][0] - price) / price) * 100
        if distance_pct > 0.5:
            score += 2
            reasons.append(f"Room to {targets[0][1]}")
        elif distance_pct < 0.3:
            score -= 2
            reasons.append(f"Too close to {targets[0][1]}")

    # --- Flow bias ---
    flow_data = snapshot.get("flow_data", {})
    flow_bias = flow_data.get("bias")
    if flow_bias:
        if (flow_bias.lower() == "bullish" and bias == "Long") or            (flow_bias.lower() == "bearish" and bias == "Short"):
            score += 1
            reasons.append(f"Flow bias {flow_bias} aligns")
        elif (flow_bias.lower() == "bullish" and bias == "Short") or              (flow_bias.lower() == "bearish" and bias == "Long"):
            score -= 1
            reasons.append(f"Flow bias {flow_bias} against")

    # --- Decision ---
    if score >= 7:
        decision = "trade"
    elif score == 6:
        decision = "maybe"
    else:
        decision = "no trade"

    plan = {
        "symbol": symbol,
        "bias": bias,
        "score": score,
        "decision": decision,
        "entry": price,
        "targets": targets,
        "reasons": reasons
    }
    return plan
