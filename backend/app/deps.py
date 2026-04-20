from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db


DbSession = Annotated[AsyncSession, Depends(get_db)]


class CurrentUser:
    """Placeholder for authenticated user. Sprint 1 骨架階段回傳匿名 user。"""

    id: str = "anonymous"
    email: str = "anonymous@example.com"
    role: str = "designer"


async def get_current_user() -> CurrentUser:
    # TODO (Sprint 1): 從 Authorization header 驗證 Keycloak JWT
    return CurrentUser()


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
