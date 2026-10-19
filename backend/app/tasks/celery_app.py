from celery import Celery

from app.config import settings

celery_app = Celery(
    "career_agent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=600,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Fail fast when Redis is unreachable: the API falls back to running
    # the same work synchronously instead of hanging on retries.
    broker_transport_options={
        "socket_timeout": 3,
        "socket_connect_timeout": 3,
        "retry_on_timeout": False,
    },
    result_backend_transport_options={
        "socket_timeout": 3,
        "socket_connect_timeout": 3,
        "retry_on_timeout": False,
        "retry_policy": {"max_retries": 1, "interval_start": 0, "interval_step": 0},
    },
    redis_socket_timeout=3,
    redis_socket_connect_timeout=3,
    redis_retry_on_timeout=False,
)
