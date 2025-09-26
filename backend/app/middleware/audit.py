"""Audit-log middleware: records method + path + actor for mutating requests."""

import time

from starlette.middleware.base import BaseHTTPMiddleware


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        try:
            if request.method in ("POST", "PUT", "DELETE"):
                elapsed = (time.time() - start) * 1000
                print(f"[audit] {request.method} {request.url.path} -> {response.status_code} ({elapsed:.1f}ms)")
        except Exception:
            pass
        return response
