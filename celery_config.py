
from celery import Celery

# Optimize Celery worker configuration
celery_app = Celery(
    'bot_management',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Celery configuration for high performance
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    result_expires=3600,  # Cached results expire after 1 hour
    task_track_started=True,
    worker_concurrency=4,  # Number of worker threads
    worker_prefetch_multiplier=1  # Process tasks one at a time per worker
)

@celery_app.task(bind=True)
def optimized_task(self, message):
    try:
        print(f"Processing message: {message}")
        # Mocked task execution
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
