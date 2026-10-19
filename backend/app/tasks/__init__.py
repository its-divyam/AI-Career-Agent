from app.tasks import analysis_tasks  # noqa: F401 -- register tasks on the Celery app
from app.tasks.celery_app import celery_app

__all__ = ["analysis_tasks", "celery_app"]
