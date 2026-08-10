# tasks.py
import base64
import os

import redis as redis_lib
from celery import Celery

from upscale import upscale

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

# Redis-клиент для хранения готовых файлов (в памяти, не на диске!)
redis_client = redis_lib.Redis.from_url(REDIS_URL)


@celery_app.task(bind=True)
def upscale_task(self, image_b64: str) -> dict:
    """Фоновая задача: апскейл изображения, результат кладём в Redis."""
    image_bytes = base64.b64decode(image_b64)
    result_bytes = upscale(image_bytes)

    filename = f"{self.request.id}.png"
    redis_client.set(f"processed:{filename}", result_bytes)
    return {"file": filename}