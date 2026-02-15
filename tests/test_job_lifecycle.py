import uuid
from unittest.mock import patch

from app.workers.tasks import update_job


def test_update_job_no_crash():
    fake_id = str(uuid.uuid4())
    with patch('app.workers.tasks.SessionLocal') as session:
        db = session.return_value
        db.get.return_value = None
        update_job(fake_id, 'running', 0.5)
        db.close.assert_called_once()
