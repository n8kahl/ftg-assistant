from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from services.security import require_secret

router = APIRouter(dependencies=[Depends(require_secret)])

class OptionsOverlay(BaseModel):
    product: str
    dte: int
    delta_target: float
    type: str  # calls | puts

class RiskBlock(BaseModel):
    r_unit: float = 1.0
    time_stop_min: int = 120

class PlanResponse(BaseModel):
    symbol: str
    bias: str
    confluence_score: float
    confidence: str
    reasons: List[str]
    entry: float
    stop: float
    targets: List[float]
    ttl_min: int
    invalidations: List[str]
    options_overlay: OptionsOverlay
    risk: RiskBlock

class FixResponse(BaseModel):
    action: str
    plan: PlanResponse

class ScreenshotAnalysis(BaseModel):
    parsed: dict
    fix: FixResponse

def _stub_price(symbol: str) -> float:
    return {
        "SPY": 556.0, "QQQ": 477.0, "TSLA": 250.0, "AMD": 170.0,
        "SPX": 5560.0, "NDX": 20000.0
    }.get(symbol.upper(), 100.0)

def _build_plan(symbol: str) -> PlanResponse:
    px = _stub_price(symbol)
    atr = max(0.5, 0.003 * px)
    bias = "long"
    entry = round(px - 0.25 * atr, 2)
    stop  = round(entry - 0.8 * atr, 2)
    targets = [round(px + 0.5 * atr, 2), round(px + 1.0 * atr, 2)]
    reasons = [
        "EMA 9/21 aligned up on 15m & 1h (stub)",
        "MACD histogram rising on 5m (stub)",
        "Within 0.3 ATR of PDH retest (stub)"
    ]
    score = 7.6
    return PlanResponse(
        symbol=symbol.upper(),
        bias=bias,
        confluence_score=score,
        confidence="medium",
        reasons=reasons,
        entry=entry,
        stop=stop,
        targets=targets,
        ttl_min=30,
        invalidations=["close below 21EMA(5m)"],
        options_overlay=OptionsOverlay(
            product=symbol.upper() if symbol.upper() in {"SPY","QQQ","TSLA","AMD"} else "SPX",
            dte=3, delta_target=0.45, type="calls"
        ),
        risk=RiskBlock(),
    )

@router.get("/plan_action", response_model=PlanResponse)
async def plan_action(symbol: Optional[str] = None):
    sym = (symbol or "SPY").upper()
    return _build_plan(sym)

@router.get("/fix_action", response_model=FixResponse)
async def fix_action(
    symbol: str,
    side: str,  # "calls" | "puts" | "shares"
    qty: Optional[float] = None,
    avg_price: Optional[float] = None,
    strike: Optional[float] = None,
    dte: Optional[int] = None,
):
    plan = _build_plan(symbol)
    if side == "shares":
        action = "add_protective_put"
        plan.options_overlay.type = "puts"
        plan.options_overlay.dte = 3
        plan.options_overlay.delta_target = 0.40
        plan.reasons.append("Protective put to cap downside (stub)")
    elif side == "calls":
        action = "convert_to_debit_vertical"
        plan.reasons.append("Convert to vertical to reduce theta (stub)")
    elif side == "puts":
        action = "roll_out_or_convert_to_spread"
        plan.reasons.append("Roll for credit or convert to spread (stub)")
    else:
        action = "review_and_flatten"
        plan.reasons.append("Unknown side; consider flattening on invalidation (stub)")
    return FixResponse(action=action, plan=plan)

@router.post("/analyze_screenshot", response_model=ScreenshotAnalysis)
async def analyze_screenshot(file: UploadFile = File(None), file_url: Optional[str] = None):
    parsed = {
        "detected": True,
        "via": "file" if file is not None else "url",
        "url": file_url
    }
    fix = await fix_action(symbol="QQQ", side="calls", qty=1, avg_price=1.35)
    return ScreenshotAnalysis(parsed=parsed, fix=fix)

@router.get("/watch_start")
async def watch_start(symbol: str, entry: float, stop: float, targets: str, ttl_min: int = 60):
    _ = [float(x) for x in targets.split(",") if x]
    return {"watcher_id": f"watch_{symbol.lower()}"}
