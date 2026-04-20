"""OIDC token verification middleware (Keycloak).

Sprint 1 骨架：只檢查 Authorization header 存在，不做真的 JWT 驗證。
Sprint 4 會接真的 Keycloak JWKS。
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # TODO (Sprint 4): 驗證 Keycloak JWT，attach user to request.state
        return await call_next(request)
