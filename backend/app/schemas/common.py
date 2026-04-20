"""Common API I/O schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectOut(ORMModel):
    id: UUID
    name: str
    owner_id: UUID | None = None
    created_at: datetime


class SpaceOut(ORMModel):
    id: UUID
    project_id: UUID
    name: str
    plan_file_id: UUID | None = None
    elevation_file_id: UUID | None = None
    parsed_plan: dict[str, Any] | None = None
    created_at: datetime


class FileOut(ORMModel):
    id: UUID
    s3_key: str
    kind: str
    size_bytes: int | None = None


class StyleOut(ORMModel):
    id: UUID
    name: str
    kind: str
    schema_json: dict[str, Any]
    created_at: datetime


class RenderOut(ORMModel):
    id: UUID
    space_id: UUID
    style_id: UUID
    status: str
    phase_percent: int
    settings: dict[str, Any]
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None
    output_file_ids: list[UUID] = []
    created_at: datetime


class PresignRequest(BaseModel):
    filename: str
    contentType: str
    kind: str


class PresignResponse(BaseModel):
    url: str
    fileId: UUID
    expiresAt: datetime


class JobReport(BaseModel):
    status: str
    phase: str | None = None
    percent: int = 0
    error: str | None = None


class AgentRegisterRequest(BaseModel):
    machineName: str
    osVersion: str
    sketchupVersion: str
    vrayVersion: str
    gpu: str | None = None


class AgentRegisterResponse(BaseModel):
    agentId: UUID
    token: str


class AgentHeartbeat(BaseModel):
    agentId: UUID
    cpu: float
    gpu: float | None = None
    diskFree: int | None = None
