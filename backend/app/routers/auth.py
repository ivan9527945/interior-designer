from fastapi import APIRouter
from pydantic import BaseModel

from app.deps import CurrentUserDep
from app.schemas.common import SessionResponse

router = APIRouter(prefix="/auth", tags=["auth"])


class SessionRequest(BaseModel):
    code: str
    state: str


@router.post("/session", response_model=SessionResponse)
async def create_session(_: SessionRequest, user: CurrentUserDep):
    # Sprint 4: OIDC callback。現在回匿名 session 讓前端能繼續。
    return SessionResponse(userId=user.id, email=user.email, role=user.role)


@router.get("/me", response_model=SessionResponse)
async def me(user: CurrentUserDep):
    return SessionResponse(userId=user.id, email=user.email, role=user.role)
