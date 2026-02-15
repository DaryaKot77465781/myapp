from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import LearningItem, Recommendation
from app.services.qdrant_service import QdrantService


def generate_rag_recommendations(db: Session, plan_id, gaps: list[dict]) -> list[Recommendation]:
    qdrant = QdrantService()
    top_gaps = ', '.join(g['skill_name'] for g in gaps[:3]) or 'general backend'
    hits = qdrant.search_learning(top_gaps, limit=5)

    db.execute(delete(Recommendation).where(Recommendation.plan_id == plan_id))
    recs = []
    for idx, hit in enumerate(hits, start=1):
        item = db.get(LearningItem, int(hit.id))
        if not item:
            continue
        rec = Recommendation(
            plan_id=plan_id,
            learning_item_id=item.id,
            rank=idx,
            rationale=f'Recommended for gaps: {top_gaps}',
            confidence=min(0.99, max(0.5, hit.score)),
            citations=[{'chunk_id': str(hit.id), 'source_title': item.title}],
        )
        db.add(rec)
        recs.append(rec)
    db.commit()
    return recs


def list_recommendations(db: Session, plan_id):
    return db.execute(select(Recommendation).where(Recommendation.plan_id == plan_id).order_by(Recommendation.rank)).scalars().all()
