from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db


DbSession = Annotated[AsyncSession, Depends(get_db)]


@dataclass
class CurrentUser:
    """Sprint 1 骨架階段：回匿名 user。Sprint 4 接 Keycloak JWT 後填真值。"""

    id: UUID | None = None
    email: str = "anonymous@example.com"
    role: str = "designer"


async def get_current_user() -> CurrentUser:
    return CurrentUser()


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
