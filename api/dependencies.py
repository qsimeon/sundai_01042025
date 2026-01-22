from fastapi import Depends, Header, HTTPException, status

from api.config import settings


async def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify API key from request header"""
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return x_api_key
