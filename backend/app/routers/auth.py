from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class SessionRequest(BaseModel):
    code: str
    state: str


@router.post("/session")
async def create_session(_: SessionRequest):
    # TODO (Sprint 1): OIDC callback，換 Keycloak JWT
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
