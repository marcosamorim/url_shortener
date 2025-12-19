import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, status

from app.core.config import settings

_requests: Dict[str, Deque[float]] = defaultdict(deque)


def enforce_rate_limit(key: str) -> None:
    if not settings.RATE_LIMIT_ENABLED:
        return

    now = time.monotonic()
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    limit = settings.RATE_LIMIT_REQUESTS

    bucket = _requests[key]
    while bucket and (now - bucket[0]) > window:
        bucket.popleft()

    if len(bucket) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    bucket.append(now)
