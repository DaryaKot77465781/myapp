import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Profile(Base):
    __tablename__ = 'profiles'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    raw_resume_text: Mapped[str | None] = mapped_column(Text)
    parsed_json: Mapped[dict | None] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Skill(Base):
    __tablename__ = 'skills'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(255), unique=True)
    taxonomy: Mapped[str | None] = mapped_column(String(50))
    external_id: Mapped[str | None] = mapped_column(String(255))
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)


class UserSkill(Base):
    __tablename__ = 'user_skills'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('profiles.id'), nullable=False)
    skill_id: Mapped[int | None] = mapped_column(ForeignKey('skills.id'))
    raw_name: Mapped[str] = mapped_column(String(255))
    level_estimate: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    evidence: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    family: Mapped[str | None] = mapped_column(String(100))
    level: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)


class RoleRequirement(Base):
    __tablename__ = 'role_requirements'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey('skills.id'), nullable=False)
    required_level: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float)
    must_have: Mapped[bool] = mapped_column(Boolean, default=False)


class Plan(Base):
    __tablename__ = 'plans'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('profiles.id'), nullable=False)
    target_role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    params_json: Mapped[dict | None] = mapped_column(JSON)
    plan_json: Mapped[dict | None] = mapped_column(JSON)
    progress_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LearningItem(Base):
    __tablename__ = 'learning_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500))
    skill_tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    level: Mapped[str | None] = mapped_column(String(50))
    duration: Mapped[str | None] = mapped_column(String(50))
    language: Mapped[str | None] = mapped_column(String(50))
    price_type: Mapped[str | None] = mapped_column(String(50))
    content_text: Mapped[str] = mapped_column(Text)


class Recommendation(Base):
    __tablename__ = 'recommendations'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('plans.id'), nullable=False)
    learning_item_id: Mapped[int] = mapped_column(ForeignKey('learning_items.id'), nullable=False)
    rank: Mapped[int] = mapped_column(Integer)
    rationale: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    citations: Mapped[list[dict]] = mapped_column(JSON, default=list)


class Job(Base):
    __tablename__ = 'jobs'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default='queued')
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    result_ref: Mapped[str | None] = mapped_column(String(255))
