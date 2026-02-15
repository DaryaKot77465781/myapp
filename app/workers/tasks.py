import uuid

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models import Job, Plan, Profile, UserSkill
from app.services.gap_analysis import compute_gap_summary
from app.services.llm import MockLLMClient, extract_skills, generate_roadmap
from app.services.recommendations import generate_rag_recommendations
from app.services.skill_mapping import normalize_skill



def update_job(job_id: str, status: str, progress: float, error: str | None = None, result_ref: str | None = None):
    db = SessionLocal()
    try:
        job = db.get(Job, uuid.UUID(job_id))
        if not job:
            return
        job.status = status
        job.progress = progress
        job.error = error
        job.result_ref = result_ref
        db.commit()
    finally:
        db.close()


def run_skill_extraction(job_id: str, profile_id: str):
    db = SessionLocal()
    try:
        update_job(job_id, 'running', 0.1)
        profile = db.get(Profile, uuid.UUID(profile_id))
        if not profile or not profile.raw_resume_text:
            raise ValueError('Profile resume missing')
        llm = MockLLMClient()
        result = extract_skills(llm, profile.raw_resume_text)
        db.execute(delete(UserSkill).where(UserSkill.profile_id == profile.id))
        for item in result.skills:
            mapped = normalize_skill(db, item.raw_name)
            db.add(UserSkill(
                profile_id=profile.id,
                skill_id=mapped.id if mapped else None,
                raw_name=item.raw_name,
                level_estimate=item.level_estimate,
                confidence=item.confidence,
                evidence=item.evidence_snippets,
            ))
        db.commit()
        update_job(job_id, 'done', 1.0, result_ref=str(profile.id))
    except Exception as exc:
        update_job(job_id, 'failed', 1.0, error=str(exc))
        raise
    finally:
        db.close()


def run_plan_generation(job_id: str, plan_id: str):
    db = SessionLocal()
    try:
        update_job(job_id, 'running', 0.2)
        plan = db.get(Plan, uuid.UUID(plan_id))
        if not plan:
            raise ValueError('plan missing')
        gap = compute_gap_summary(db, plan.profile_id, plan.target_role_id)
        llm = MockLLMClient()
        roadmap = generate_roadmap(llm, str(gap))
        plan.plan_json = {**roadmap.model_dump(), **gap}
        plan.progress_json = {'done_actions': []}
        db.commit()
        update_job(job_id, 'done', 1.0, result_ref=str(plan.id))
    except Exception as exc:
        update_job(job_id, 'failed', 1.0, error=str(exc))
        raise
    finally:
        db.close()


def run_recommendations(job_id: str, plan_id: str):
    db = SessionLocal()
    try:
        update_job(job_id, 'running', 0.3)
        plan = db.get(Plan, uuid.UUID(plan_id))
        if not plan:
            raise ValueError('plan missing')
        gaps = (plan.plan_json or {}).get('gaps', [])
        generate_rag_recommendations(db, plan.id, gaps)
        update_job(job_id, 'done', 1.0, result_ref=str(plan.id))
    except Exception as exc:
        update_job(job_id, 'failed', 1.0, error=str(exc))
        raise
    finally:
        db.close()
