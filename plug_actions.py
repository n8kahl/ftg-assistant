from fastapi import APIRouter
from services import features_snapshot

router = APIRouter()

@router.get("/features_snapshot")
async def get_features_snapshot(symbol: str):
    return await features_snapshot.get_snapshot(symbol)
