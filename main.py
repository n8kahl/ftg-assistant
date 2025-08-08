from fastapi import FastAPI
from plug_actions import router as actions_router

app = FastAPI()

app.include_router(actions_router)

@app.get("/")
async def root():
    return {"status": "ok"}
