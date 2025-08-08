from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

APP_NAME = "ftg-assistant"
CT = ZoneInfo("America/Chicago")

app = FastAPI(title="FTG Assistant API", version="0.4.0")

@app.get("/")
def root():
    return {"ok": True, "service": APP_NAME, "ts_ct": datetime.now(CT).isoformat()}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/_routes")
def routes() -> List[dict]:
    out = []
    for r in app.routes:
        methods = sorted(list(getattr(r, "methods", []))) if getattr(r, "methods", None) else None
        path = getattr(r, "path", getattr(r, "path_format", ""))
        name = getattr(r, "name", "")
        out.append({"path": path, "methods": methods, "name": name})
    return JSONResponse(out)

# === Chat-Data Actions router ===
from plug_actions import router as actions_router
app.include_router(actions_router)
