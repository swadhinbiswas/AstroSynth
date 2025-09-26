"""Simple in-memory sliding-window rate limiter (per-IP)."""

import time
from collections import defaultdict

from fastapi import HTTPException, Request

_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit(request: Request, limit_per_minute: int = 60) -> None:
    now = time.time()
    key = request.client.host if request.client else "unknown"
    window = [t for t in _hits[key] if now - t < 60]
    if len(window) >= limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Slow down, explorer.")
    window.append(now)
    _hits[key] = window
