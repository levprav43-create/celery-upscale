# tasks.py
import os

import redis as redis_lib
from celery import Celery

from upscale import upscale

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Время жизни результата в Redis — 1 час (чтобы память не переполнялась)
RESULT_TTL = 3600

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    # pickle позволяет передавать БАЙТЫ напрямую — без base64 и лишних операций.
    # Безопасно: писать в наш Redis могут только наши сервисы.
    task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["pickle", "json"],
)

redis_client = redis_lib.Redis.from_url(REDIS_URL)


@celery_app.task(bind=True)
def upscale_task(self, image_bytes: bytes) -> dict:
    """Фоновая задача: апскейл изображения, результат в Redis с TTL."""
    result_bytes = upscale(image_bytes)

    filename = f"{self.request.id}.png"
    redis_client.set(f"processed:{filename}", result_bytes, ex=RESULT_TTL)
    return {"file": filename}