import os
from fastapi import Header, HTTPException, status

_X_SECRET = os.getenv("X_API_SECRET")

async def require_secret(x_api_secret: str | None = Header(default=None)):
    # If no secret is set (dev), allow requests
    if not _X_SECRET:
        return
    if x_api_secret != _X_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
