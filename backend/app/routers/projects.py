from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.deps import CurrentUserDep, DbSession
from app.models.space import Space
from app.models.project import Project
from app.schemas.common import CreateSpaceRequest, ProjectOut, SpaceOut

router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: DbSession, user: CurrentUserDep):
    result = await db.execute(
        select(Project).where(Project.archived_at.is_(None)).order_by(Project.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(body: CreateProjectRequest, db: DbSession, user: CurrentUserDep):
    project = Project(name=body.name, owner_id=user.id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: UUID, db: DbSession, user: CurrentUserDep):
    row = await db.get(Project, project_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    return row


@router.post("/{project_id}/spaces", response_model=SpaceOut, status_code=status.HTTP_201_CREATED)
async def create_space(project_id: UUID, body: CreateSpaceRequest, db: DbSession, user: CurrentUserDep):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    space = Space(
        project_id=project_id,
        name=body.name,
        plan_file_id=body.planFileId,
        elevation_file_id=body.elevationFileId,
    )
    db.add(space)
    await db.commit()
    await db.refresh(space)
    return space


@router.get("/{project_id}/spaces", response_model=list[SpaceOut])
async def list_spaces(project_id: UUID, db: DbSession, user: CurrentUserDep):
    result = await db.execute(
        select(Space).where(Space.project_id == project_id).order_by(Space.created_at)
    )
    return result.scalars().all()
