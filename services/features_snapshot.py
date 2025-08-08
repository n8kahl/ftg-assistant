from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends
from services.security import require_secret
from services import data_polygon, features, levels, options_picker
from services import vwap as vwap_utils
import pandas as pd
import math

router = APIRouter(dependencies=[Depends(require_secret)])

@router.get("/features_snapshot")
async def features_snapshot(symbol: str) -> Dict[str, Any]:
    sym = symbol.upper()
    # Pull data
    df1 = await data_polygon.get_agg(sym, "1m")
    df5 = await data_polygon.get_agg(sym, "5m")
    df15 = await data_polygon.get_agg(sym, "15m")
    df1h = await data_polygon.get_agg(sym, "1h")
    dfd = await data_polygon.get_agg(sym, "D")

    # Compute indicators
    f1 = features.compute_all(df1) if not df1.empty else df1
    f5 = features.compute_all(df5) if not df5.empty else df5
    f15 = features.compute_all(df15) if not df15.empty else df15
    f1h = features.compute_all(df1h) if not df1h.empty else df1h
    fd = features.compute_all(dfd) if not dfd.empty else dfd

    price = float(f5['close'].iloc[-1]) if not f5.empty else (float(f1['close'].iloc[-1]) if not f1.empty else None)
    atr = float(f5['atr14'].iloc[-1]) if (not f5.empty and not math.isnan(f5['atr14'].iloc[-1])) else None

    # Session & Anchored VWAPs
    svwap = vwap_utils.session_vwap(f1) if not f1.empty else None
    or5h, or5l = vwap_utils.opening_range(f1, 5) if not f1.empty else (None, None)
    or15h, or15l = vwap_utils.opening_range(f1, 15) if not f1.empty else (None, None)
    # Anchors we can compute today reliably: session open, OR5H/OR5L once formed
    anchors = {}
    if not f1.empty:
        so = vwap_utils.session_open_ts(f1)
        if so is not None:
            anchors["session_open"] = {"ts": so.isoformat(), "vwap": vwap_utils.anchored_vwap(f1, so)}
        # We approximate OR anchors by using the first time the bound was printed
        # For simplicity in this MVP we just expose OR levels; anchoring exact timestamp can be added later.
    pdh, pdl = levels.prev_day_levels(fd)

    # Options candidates (best effort)
    primary, alt = await options_picker.pick(symbol=sym if sym in ["SPY","QQQ","TSLA","AMD"] else "SPY",
                                             bias="long", dte_target=3, delta_target=0.45)
    candidates = []
    if primary:
        candidates.append(primary)
    if alt:
        candidates.append(alt)

    out = {
        "symbol": sym,
        "price": price,
        "atr14_5m": atr,
        "emas": {
            "5m": {k: float(f5[k].iloc[-1]) for k in ["ema9","ema21","ema50","ema200"]} if not f5.empty else None,
            "15m": {k: float(f15[k].iloc[-1]) for k in ["ema9","ema21","ema50","ema200"]} if not f15.empty else None,
            "1h": {k: float(f1h[k].iloc[-1]) for k in ["ema9","ema21","ema50","ema200"]} if not f1h.empty else None,
        },
        "momentum_5m": {
            "rsi14": (float(f5["rsi14"].iloc[-1]) if not f5.empty else None),
            "macd_hist": (float(f5["macd_hist"].iloc[-1]) if not f5.empty else None)
        },
        "levels": {
            "pdh": pdh, "pdl": pdl,
            "or5": {"high": or5h, "low": or5l},
            "or15": {"high": or15h, "low": or15l},
        },
        "vwap": {
            "session": svwap,
            "anchors": anchors
        },
        "options_candidates": candidates
    }
    return out
