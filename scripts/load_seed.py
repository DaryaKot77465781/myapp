import json
from pathlib import Path

from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models import LearningItem, Role, RoleRequirement, Skill
from app.services.qdrant_service import QdrantService


def load_json(name: str):
    return json.loads((Path('seed') / name).read_text())


def main() -> None:
    db = SessionLocal()
    qdrant = QdrantService()
    try:
        db.execute(delete(RoleRequirement))
        db.execute(delete(Role))
        db.execute(delete(Skill))
        db.execute(delete(LearningItem))
        db.commit()

        for row in load_json('skills.json'):
            db.add(Skill(**row))
        for row in load_json('roles.json'):
            db.add(Role(**row))
        for row in load_json('role_requirements.json'):
            db.add(RoleRequirement(**row))
        for row in load_json('learning_items.json'):
            item = LearningItem(**row)
            db.add(item)
        db.commit()

        for item in db.query(LearningItem).all():
            qdrant.upsert_learning_item(item.id, item.content_text, {'title': item.title, 'url': item.url})
        print('Seed loaded')
    finally:
        db.close()


if __name__ == '__main__':
    main()
