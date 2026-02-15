from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Skill


def normalize_skill(db: Session, raw_skill: str) -> Skill | None:
    normalized = raw_skill.strip().lower()
    skills = db.execute(select(Skill)).scalars().all()
    for skill in skills:
        names = [skill.canonical_name.lower(), *(a.lower() for a in skill.aliases or [])]
        if normalized in names:
            return skill
    for skill in skills:
        if normalized in skill.canonical_name.lower():
            return skill
    return None
