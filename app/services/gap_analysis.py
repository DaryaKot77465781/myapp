from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RoleRequirement, Skill, UserSkill


def compute_gap_summary(db: Session, profile_id, target_role_id: int) -> dict:
    reqs = db.execute(select(RoleRequirement).where(RoleRequirement.role_id == target_role_id)).scalars().all()
    user_skills = db.execute(select(UserSkill).where(UserSkill.profile_id == profile_id)).scalars().all()
    current = {us.skill_id: us.level_estimate for us in user_skills if us.skill_id}

    total_weighted_required = 0.0
    total_weighted_gap = 0.0
    gaps = []
    must_have_missing = []

    for req in reqs:
        curr = float(current.get(req.skill_id, 0.0))
        gap = max(0.0, req.required_level - curr)
        weighted_gap = req.weight * gap
        total_weighted_required += req.weight * req.required_level
        total_weighted_gap += weighted_gap
        skill_name = db.get(Skill, req.skill_id).canonical_name
        if gap > 0:
            gaps.append({
                'skill_id': req.skill_id,
                'skill_name': skill_name,
                'required_level': req.required_level,
                'current_level': curr,
                'priority': min(5, max(1, int(round(req.weight * gap)))),
                'rationale': f'Need +{gap:.1f} proficiency to meet role expectation.'
            })
        if req.must_have and gap > 0:
            must_have_missing.append({
                'skill_id': req.skill_id,
                'skill_name': skill_name,
                'required_level': req.required_level,
                'current_level': curr,
            })

    coverage = 1.0 if total_weighted_required == 0 else 1 - (total_weighted_gap / total_weighted_required)
    return {
        'coverage_score': max(0.0, min(1.0, coverage)),
        'must_have_missing': must_have_missing,
        'gaps': sorted(gaps, key=lambda x: (-x['priority'], x['skill_name'])),
    }
