import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_api_key
from app.db.session import get_db
from app.models import Job, Plan, Profile, Recommendation, User, UserSkill
from app.schemas.contracts import JobResponse, PlanCreate, ProfileCreate, ProgressPatch, ResumeTextPayload, UserCreate
from app.services.gap_analysis import compute_gap_summary
from app.services.llm import MockLLMClient, intake_check
from app.services.resume_parser import extract_text_from_upload
from app.workers.queue import enqueue
from app.workers.tasks import run_plan_generation, run_recommendations, run_skill_extraction

router = APIRouter(prefix='/v1', dependencies=[Depends(require_api_key)])


@router.post('/users')
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(id=payload.user_id or uuid.uuid4())
    db.add(user)
    db.commit()
    return {'id': user.id}


@router.post('/profiles')
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(404, 'User not found')
    profile = Profile(user_id=payload.user_id)
    db.add(profile)
    db.commit()
    return {'id': profile.id}


@router.post('/profiles/{profile_id}/resume')
async def upload_resume(profile_id: uuid.UUID, db: Session = Depends(get_db), file: UploadFile | None = File(default=None), text: str | None = Form(default=None)):
    profile = db.get(Profile, profile_id)
    if not profile:
        raise HTTPException(404, 'Profile not found')
    if file:
        content = await file.read()
        parsed = extract_text_from_upload(file.filename or 'unknown', content)
    elif text:
        parsed = text
    else:
        raise HTTPException(400, 'Provide file or text')
    profile.raw_resume_text = parsed
    db.commit()
    return {'profile_id': profile.id, 'chars': len(parsed)}


@router.post('/profiles/{profile_id}/intake-check')
def run_intake_check(profile_id: uuid.UUID, db: Session = Depends(get_db)):
    profile = db.get(Profile, profile_id)
    if not profile or not profile.raw_resume_text:
        raise HTTPException(400, 'Missing resume')
    result = intake_check(MockLLMClient(), profile.raw_resume_text)
    profile.parsed_json = {'intake_check': result.model_dump()}
    db.commit()
    return result


@router.post('/profiles/{profile_id}/skills', response_model=JobResponse)
def enqueue_skills(profile_id: uuid.UUID, db: Session = Depends(get_db)):
    if not db.get(Profile, profile_id):
        raise HTTPException(404, 'Profile not found')
    job = Job(type='skills')
    db.add(job)
    db.commit()
    enqueue(run_skill_extraction, str(job.id), str(profile_id))
    return JobResponse(job_id=job.id, status=job.status)


@router.get('/profiles/{profile_id}/skills')
def get_profile_skills(profile_id: uuid.UUID, db: Session = Depends(get_db)):
    skills = db.execute(select(UserSkill).where(UserSkill.profile_id == profile_id)).scalars().all()
    return {'skills': [{
        'raw_name': s.raw_name,
        'canonical_skill_id': s.skill_id,
        'level_estimate': s.level_estimate,
        'confidence': s.confidence,
        'evidence_snippets': s.evidence,
    } for s in skills]}


@router.post('/plans', response_model=JobResponse)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    plan = Plan(user_id=payload.user_id, profile_id=payload.profile_id, target_role_id=payload.target_role_id, params_json=payload.params_json)
    db.add(plan)
    job = Job(type='plan')
    db.add(job)
    db.commit()
    enqueue(run_plan_generation, str(job.id), str(plan.id))
    return JobResponse(job_id=job.id, status=job.status)


@router.get('/plans/{plan_id}')
def get_plan(plan_id: uuid.UUID, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, 'Plan not found')
    gap_summary = compute_gap_summary(db, plan.profile_id, plan.target_role_id)
    return {'plan_id': plan.id, 'plan_json': plan.plan_json, 'gap_summary': gap_summary}


@router.post('/plans/{plan_id}/recommendations', response_model=JobResponse)
def enqueue_plan_recommendations(plan_id: uuid.UUID, db: Session = Depends(get_db)):
    if not db.get(Plan, plan_id):
        raise HTTPException(404, 'Plan not found')
    job = Job(type='recommendations')
    db.add(job)
    db.commit()
    enqueue(run_recommendations, str(job.id), str(plan_id))
    return JobResponse(job_id=job.id, status=job.status)


@router.get('/plans/{plan_id}/recommendations')
def get_recommendations(plan_id: uuid.UUID, db: Session = Depends(get_db)):
    recs = db.execute(select(Recommendation).where(Recommendation.plan_id == plan_id).order_by(Recommendation.rank)).scalars().all()
    return {'items': [{
        'learning_item_id': r.learning_item_id,
        'rank': r.rank,
        'rationale': r.rationale,
        'confidence': r.confidence,
        'citations': r.citations,
    } for r in recs]}


@router.patch('/plans/{plan_id}/progress')
def patch_progress(plan_id: uuid.UUID, payload: ProgressPatch, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, 'Plan not found')
    progress = plan.progress_json or {'done_actions': []}
    done_actions: set[str] = set(progress.get('done_actions', []))
    if payload.done:
        done_actions.add(payload.action_title)
    else:
        done_actions.discard(payload.action_title)
    progress['done_actions'] = sorted(done_actions)
    plan.progress_json = progress
    db.commit()
    return progress


@router.get('/jobs/{job_id}')
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, 'Job not found')
    return {
        'job_id': job.id,
        'status': job.status,
        'progress': job.progress,
        'error': job.error,
        'result_ref': job.result_ref,
    }
