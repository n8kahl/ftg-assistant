import math
from services.schema import PlanResponse, OptionsOverlay, RiskBlock, OptionsDetail, OptionContract
from services import market_data as data_polygon, features, levels, confluence, options_picker

def pick_best_symbol() -> str:
    return "SPY"

async def _tf_df(symbol: str, tf: str):
    df = await data_polygon.get_agg(symbol, tf)
    return features.compute_all(df)

async def generate_plan(symbol: str) -> PlanResponse:
    sym = symbol.upper()
    df5 = await _tf_df(sym, "5m")
    df15 = await _tf_df(sym, "15m")
    df1h = await _tf_df(sym, "1h")
    dfd = await _tf_df(sym, "D")
    if df5.empty or df15.empty or df1h.empty or dfd.empty:
        last = float(df5["close"].iloc[-1]) if not df5.empty else 100.0
        return PlanResponse(
            symbol=sym, bias="long", reasons=["data unavailable"], entry=round(last-0.25,2), stop=round(last-1.0,2),
            targets=[round(last+0.5,2),round(last+1.0,2)], ttl_min=30,
            options_overlay=OptionsOverlay(product=sym if sym in ["SPY","QQQ","TSLA","AMD"] else "SPX", dte=3, delta_target=0.45, type="calls"),
            risk=RiskBlock(),
        )
    def stack_up(df): return df["ema9"].iloc[-1] > df["ema21"].iloc[-1] > df["ema50"].iloc[-1]
    def stack_down(df): return df["ema9"].iloc[-1] < df["ema21"].iloc[-1] < df["ema50"].iloc[-1]
    up = stack_up(df15) and stack_up(df1h)
    down = stack_down(df15) and stack_down(df1h)
    bias = "long" if up and not down else "short" if down and not up else "long"

    macd_hist = df5["macd_hist"].iloc[-3:]
    rsi5 = df5["rsi14"].iloc[-1]
    momentum_ok = (macd_hist.diff().iloc[-1] > 0) and ((rsi5 > 50) if bias=="long" else (rsi5 < 50))

    pdh, pdl = levels.prev_day_levels(dfd)
    close = float(df5["close"].iloc[-1])
    atr = float(df5["atr14"].iloc[-1]) if not math.isnan(df5["atr14"].iloc[-1]) else max(0.5, 0.003*close)
    prox = 0.3 * atr
    level_ok = False
    if pdh and pdl:
        level_ok = (abs(close - pdh) <= prox) or (abs(close - pdl) <= prox)

    atr_sma = df5["atr14"].rolling(20).mean().iloc[-1]
    vol_ok = bool(atr_sma and (0.6*atr_sma <= df5["atr14"].iloc[-1] <= 1.8*atr_sma))

    score = confluence.score_from_signals(bias_ok=(up if bias=="long" else down),
                                          momentum_ok=momentum_ok,
                                          level_ok=level_ok, vol_ok=vol_ok)

    if bias == "long":
        entry = round(close - 0.25*atr, 2)
        stop = round(entry - 0.8*atr, 2)
        targets = [round(close + 0.5*atr, 2), round(close + 1.0*atr, 2)]
    else:
        entry = round(close + 0.25*atr, 2)
        stop = round(entry + 0.8*atr, 2)
        targets = [round(close - 0.5*atr, 2), round(close - 1.0*atr, 2)]

    reasons = []
    if bias=="long":
        reasons.append("15m & 1h EMA9>21>50 aligned up")
        reasons.append("MACD hist rising on 5m; RSI>50")
    else:
        reasons.append("15m & 1h EMA9<21<50 aligned down")
        reasons.append("MACD hist falling on 5m; RSI<50")
    if level_ok: reasons.append("Within 0.3 ATR of PDH/PDL")
    if vol_ok: reasons.append("ATR in normal regime")

    overlay = OptionsOverlay(product=sym if sym in ["SPY","QQQ","TSLA","AMD"] else "SPX",
                             dte=3, delta_target=0.45, type=("calls" if bias=="long" else "puts"))
    primary, alt = await options_picker.pick(symbol=sym if sym in ["SPY","QQQ","TSLA","AMD"] else "SPY",
                                             bias=bias, dte_target=overlay.dte, delta_target=overlay.delta_target)
    detail = None
    if primary:
        from services.schema import OptionsDetail, OptionContract
        detail = OptionsDetail(primary=OptionContract(**primary),
                               vertical_alt=(OptionContract(**alt) if alt else None))

    return PlanResponse(
        symbol=sym, bias=bias, confluence_score=score, confidence="medium",
        reasons=reasons, entry=entry, stop=stop, targets=targets, ttl_min=30,
        invalidations=[("close below 21EMA(5m)" if bias=="long" else "close above 21EMA(5m)")],
        options_overlay=overlay, options_detail=detail, risk=RiskBlock(),
    )
