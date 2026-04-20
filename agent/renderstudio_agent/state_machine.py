"""Job 狀態機 — 規格 §5.3。"""

from enum import Enum


class JobState(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PARSING = "parsing"
    MODELING = "modeling"
    MATERIAL = "material"
    RENDERING = "rendering"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


_TRANSITIONS: dict[JobState, set[JobState]] = {
    JobState.PENDING: {JobState.ASSIGNED, JobState.CANCELLED},
    JobState.ASSIGNED: {JobState.PARSING, JobState.ERROR, JobState.CANCELLED},
    JobState.PARSING: {JobState.MODELING, JobState.ERROR, JobState.CANCELLED},
    JobState.MODELING: {JobState.MATERIAL, JobState.ERROR, JobState.CANCELLED},
    JobState.MATERIAL: {JobState.RENDERING, JobState.ERROR, JobState.CANCELLED},
    JobState.RENDERING: {JobState.COMPLETED, JobState.ERROR, JobState.CANCELLED},
    JobState.COMPLETED: set(),
    JobState.ERROR: set(),
    JobState.CANCELLED: set(),
}


def can_transition(frm: JobState, to: JobState) -> bool:
    return to in _TRANSITIONS.get(frm, set())
