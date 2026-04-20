from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.deps import CurrentUserDep, DbSession
from app.schemas.common import ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: DbSession, user: CurrentUserDep):
    # TODO (Sprint 1): SELECT FROM projects WHERE owner_id=user.id
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(body: CreateProjectRequest, db: DbSession, user: CurrentUserDep):
    # TODO (Sprint 1): INSERT projects
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/{project_id}/spaces")
async def create_space(project_id: str, db: DbSession, user: CurrentUserDep):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
