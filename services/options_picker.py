from typing import Optional, Tuple
from services.data_tradier import expirations, chain

MIN_OI = 500
MIN_VOL = 100
MAX_SPREAD_PCT = 0.12  # 12% of mid

def _ok(o) -> bool:
    try:
        bid = float(o["bid"]); ask = float(o["ask"])
        if bid <= 0 or ask <= 0: return False
        mid = (bid+ask)/2
        if mid <= 0: return False
        spread_pct = (ask-bid)/mid
        oi = int(o.get("open_interest") or 0)
        vol = int(o.get("volume") or 0)
        return spread_pct <= MAX_SPREAD_PCT and (oi >= MIN_OI or vol >= MIN_VOL)
    except Exception:
        return False

async def pick(symbol: str, bias: str, dte_target: int, delta_target: float) -> Tuple[Optional[dict], Optional[dict]]:
    exps = await expirations(symbol) or []
    if not exps:
        return None, None
    expiry = exps[0]
    c = await chain(symbol, expiry) or []
    side = "call" if bias == "long" else "put"
    pool = [o for o in c if o.get("option_type")==side and _ok(o)]
    if not pool:
        return None, None
    leg = min(pool, key=lambda o: abs(abs(float(o["greeks"]["delta"])) - delta_target))
    bid, ask = float(leg["bid"]), float(leg["ask"]); mid = round((bid+ask)/2, 2)
    primary = {
        "product": symbol,
        "expiry": leg["expiration_date"],
        "right": "C" if side=="call" else "P",
        "strike": float(leg["strike"]),
        "occ": leg["symbol"],
        "bid": bid, "ask": ask, "mid": mid,
        "iv": float(leg["greeks"]["mid_iv"]), "delta": abs(float(leg["greeks"]["delta"])),
        "limit": max(0.01, mid - 0.01)
    }
    alt = None
    if side == "call":
        pool2 = [o for o in c if o.get("option_type")=="call" and _ok(o)]
        if pool2:
            short = min(pool2, key=lambda o: abs(abs(float(o["greeks"]["delta"])) - 0.25))
            alt = {
                "product": symbol, "expiry": short["expiration_date"], "right":"C",
                "strike": float(short["strike"]), "occ": short["symbol"],
                "bid": float(short["bid"]), "ask": float(short["ask"]),
                "mid": round((float(short["bid"])+float(short["ask"]))/2,2),
                "iv": float(short["greeks"]["mid_iv"]), "delta": abs(float(short["greeks"]["delta"])),
                "limit": None
            }
    return primary, alt
