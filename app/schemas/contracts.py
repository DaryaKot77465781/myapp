import uuid
from typing import Literal

from pydantic import BaseModel, Field


class IntakeQuestion(BaseModel):
    id: str
    question: str
    type: Literal['text', 'single_choice', 'multi_choice']
    options: list[str] | None = None


class IntakeCheckResult(BaseModel):
    proceed: bool
    confidence: float = Field(ge=0, le=1)
    missing_fields: list[str]
    questions: list[IntakeQuestion]


class SkillExtractItem(BaseModel):
    raw_name: str
    canonical_skill_id: int | None = None
    canonical_name: str | None = None
    level_estimate: float = Field(ge=0, le=5)
    confidence: float = Field(ge=0, le=1)
    evidence_snippets: list[str]


class SkillExtractResult(BaseModel):
    skills: list[SkillExtractItem]


class Citation(BaseModel):
    chunk_id: str
    source_title: str


class MustHaveMissing(BaseModel):
    skill_id: int
    skill_name: str
    required_level: float
    current_level: float


class GapItem(BaseModel):
    skill_id: int
    skill_name: str
    required_level: float
    current_level: float
    priority: int = Field(ge=1, le=5)
    rationale: str


class RoadmapAction(BaseModel):
    type: Literal['learning', 'practice', 'social']
    title: str
    description: str
    effort_hours: int
    success_criteria: str


class RoadmapPhase(BaseModel):
    name: str
    duration_months: str
    focus_skills: list[int]
    actions: list[RoadmapAction]
    risks: list[str]


class RoadmapPlanResult(BaseModel):
    coverage_score: float = Field(ge=0, le=1)
    must_have_missing: list[MustHaveMissing]
    gaps: list[GapItem]
    phases: list[RoadmapPhase]


class RecommendationItem(BaseModel):
    learning_item_id: int
    title: str
    url: str
    mapped_skills: list[int]
    why: str
    when_in_plan_phase: str
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation]


class RecommendationResult(BaseModel):
    items: list[RecommendationItem]


class UserCreate(BaseModel):
    user_id: uuid.UUID | None = None


class ProfileCreate(BaseModel):
    user_id: uuid.UUID


class PlanCreate(BaseModel):
    user_id: uuid.UUID
    profile_id: uuid.UUID
    target_role_id: int
    params_json: dict | None = None


class ProgressPatch(BaseModel):
    action_title: str
    done: bool


class JobResponse(BaseModel):
    job_id: uuid.UUID
    status: str


class ResumeTextPayload(BaseModel):
    text: str
