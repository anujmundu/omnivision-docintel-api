"""
Security, API Key Authentication, and Token-Bucket Rate Limiting Middleware.
"""

import time
from collections import defaultdict
from fastapi import HTTPException, Security, Request, status
from fastapi.security.api_key import APIKeyHeader
from .config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# In-memory token bucket rate limiter
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.rate = requests_per_minute
        self.buckets = defaultdict(lambda: {"tokens": self.rate, "last_updated": time.time()})

    def check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        bucket = self.buckets[client_ip]
        elapsed = now - bucket["last_updated"]
        bucket["last_updated"] = now

        # Replenish tokens
        bucket["tokens"] = min(self.rate, bucket["tokens"] + elapsed * (self.rate / 60.0))

        if bucket["tokens"] >= 1.0:
            bucket["tokens"] -= 1.0
            return True
        return False


rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)


async def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
) -> str:
    # 1. Check Rate Limit
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 60 requests per minute allowed.",
        )

    # 2. Check API Key
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header. Contact administrator for credentials.",
        )

    return api_key
