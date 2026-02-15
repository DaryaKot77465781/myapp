import uuid

from redis import Redis
from rq import Queue

from app.core.config import settings

redis_conn = Redis.from_url(settings.redis_url)
queue = Queue('career-jobs', connection=redis_conn)


def enqueue(func, *args, **kwargs):
    return queue.enqueue(func, *args, **kwargs)


def to_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value)
