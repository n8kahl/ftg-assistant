from pydantic import BaseModel
from typing import List, Optional

class OptionsOverlay(BaseModel):
    product: str
    dte: int
    delta_target: float
    type: str  # calls or puts

class RiskBlock(BaseModel):
    r_unit: float = 1.0
    time_stop_min: int = 120

class OptionContract(BaseModel):
    product: str
    expiry: str
    right: str   # C or P
    strike: float
    occ: Optional[str] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    mid: Optional[float] = None
    iv: Optional[float] = None
    delta: Optional[float] = None
    limit: Optional[float] = None   # suggested limit

class OptionsDetail(BaseModel):
    primary: Optional[OptionContract] = None
    vertical_alt: Optional[OptionContract] = None

class PlanResponse(BaseModel):
    symbol: str
    bias: str
    confluence_score: float = 0.0
    confidence: str = "medium"
    reasons: List[str]
    entry: float
    stop: float
    targets: List[float]
    ttl_min: int
    invalidations: List[str] = []
    options_overlay: OptionsOverlay
    options_detail: Optional[OptionsDetail] = None
    risk: RiskBlock

class FixResponse(BaseModel):
    action: str
    plan: PlanResponse

class ScreenshotAnalysis(BaseModel):
    parsed: dict
    fix: FixResponse
