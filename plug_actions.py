from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File
from services.security import require_secret
from services.schema import PlanResponse, FixResponse, ScreenshotAnalysis
from services import strategies, fix_engine
from services.features_snapshot import router as features_router

router = APIRouter(dependencies=[Depends(require_secret)])

# mount /features_snapshot under the same guard
router.include_router(features_router)

@router.get("/plan_action", response_model=PlanResponse)
async def plan_action(symbol: Optional[str] = None):
    sym = (symbol or strategies.pick_best_symbol()).upper()
    plan = await strategies.generate_plan(sym)
    return plan

@router.get("/fix_action", response_model=FixResponse)
async def fix_action(symbol: str, side: str,
                     qty: Optional[float] = None,
                     avg_price: Optional[float] = None,
                     strike: Optional[float] = None,
                     dte: Optional[int] = None):
    return await fix_engine.propose_fix({
        "symbol": symbol, "side": side, "qty": qty,
        "avg_price": avg_price, "strike": strike, "dte": dte
    })

@router.post("/analyze_screenshot", response_model=ScreenshotAnalysis)
async def analyze_screenshot(file: UploadFile = File(None), file_url: Optional[str] = None):
    parsed = {
        "detected": True,
        "via": "file" if file is not None else "url",
        "url": file_url
    }
    fix = await fix_engine.propose_fix({"symbol":"QQQ","side":"calls","qty":1,"avg_price":1.35})
    return {"parsed": parsed, "fix": fix}

@router.get("/watch_start")
async def watch_start(symbol: str, entry: float, stop: float, targets: str, ttl_min: int = 30):
    _ = [float(x) for x in targets.split(",") if x]
    return {"watcher_id": f"watch_{symbol.lower()}"}
