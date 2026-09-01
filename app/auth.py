from fastapi import Header, HTTPException
from app.config import API_KEY, ENVIRONMENT

def require_api_key(x_api_key: str | None = Header(default=None)):
    # Local development can run without a key. Set HR_API_KEY in production.
    if ENVIRONMENT == "production":
        if not API_KEY or x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Valid API key required")
    elif API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True
